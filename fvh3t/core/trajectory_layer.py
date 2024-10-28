from __future__ import annotations

from datetime import datetime, timezone
from math import log10
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsExpression,
    QgsFeature,
    QgsFeatureIterator,
    QgsFeatureRequest,
    QgsFeatureSource,
    QgsField,
    QgsPointXY,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

from fvh3t.core.exceptions import InvalidLayerException
from fvh3t.core.trajectory import Trajectory, TrajectoryNode

UNIX_TIMESTAMP_UNIT_THRESHOLD = 13


def digits_in_timestamp_int(num: int):
    return int(log10(num)) + 1


class TrajectoryLayer:
    """
    Wrapper around a QgsVectorLayer object from which trajectories
    can be instantiated, i.e.

    1. is a point layer
    2. has a valid identifier field
    3. has a valid timestamp field
    4. has a valid width field
    5. has a valid length field
    6. has a valid height field
    """

    def __init__(
        self,
        layer: QgsVectorLayer,
        id_field: str,
        timestamp_field: str,
        width_field: str,
        length_field: str,
        height_field: str,
        timestamp_unit: QgsUnitTypes.TemporalUnit = QgsUnitTypes.TemporalUnit.TemporalUnknownUnit,
    ) -> None:
        self.__layer: QgsVectorLayer = layer
        self.__id_field: str = id_field
        self.__timestamp_field: str = timestamp_field
        self.__width_field: str = width_field
        self.__length_field: str = length_field
        self.__height_field: str = height_field

        self.__map_units: QgsUnitTypes.DistanceUnit = QgsUnitTypes.DistanceUnit.DistanceUnknownUnit
        self.__timestamp_units: QgsUnitTypes.TemporalUnit = timestamp_unit

        if self.is_valid():
            self.__map_units = self.__layer.crs().mapUnits()

            if self.__timestamp_units == QgsUnitTypes.TemporalUnit.TemporalUnknownUnit:
                first_feature = self.__layer.getFeature(1)

                # TODO: ensure that this is a numeric field
                # OR handle cases where it isn't
                timestamp: int = first_feature.attribute(self.__timestamp_field)

                # if a unix timestamp is in seconds and
                # has 13 or more digits it is in year >= 33658
                # so in this case let's assume that the
                # timestamp is actually in milliseconds
                if digits_in_timestamp_int(timestamp) >= UNIX_TIMESTAMP_UNIT_THRESHOLD:
                    self.__timestamp_units = QgsUnitTypes.TemporalUnit.TemporalMilliseconds
                else:
                    self.__timestamp_units = QgsUnitTypes.TemporalUnit.TemporalSeconds
        else:
            msg = "TrajectoryLayer could not be properly created!"
            raise InvalidLayerException(msg)

        self.__trajectories: tuple[Trajectory, ...] = ()
        self.create_trajectories()

        # TODO: should the class of traveler be handled here?

    def layer(self) -> QgsVectorLayer:
        return self.__layer

    def id_field(self) -> str:
        return self.__id_field

    def map_units(self) -> QgsUnitTypes.DistanceUnit:
        return self.__map_units

    def timestamp_units(self) -> QgsUnitTypes.TemporalUnit:
        return self.__timestamp_units

    def timestamp_field(self) -> str:
        return self.__timestamp_field

    def width_field(self) -> str:
        return self.__width_field

    def length_field(self) -> str:
        return self.__length_field

    def height_field(self) -> str:
        return self.__height_field

    def trajectories(self) -> tuple[Trajectory, ...]:
        return self.__trajectories

    def crs(self) -> QgsCoordinateReferenceSystem:
        return self.__layer.crs()

    def create_trajectories(self) -> None:
        id_field_idx: int = self.__layer.fields().indexOf(self.__id_field)
        timestamp_field_idx: int = self.__layer.fields().indexOf(self.__timestamp_field)
        width_field_idx: int = self.__layer.fields().indexOf(self.__width_field)
        length_field_idx: int = self.__layer.fields().indexOf(self.__length_field)
        height_field_idx: int = self.__layer.fields().indexOf(self.__height_field)

        unique_ids: set[Any] = self.__layer.uniqueValues(id_field_idx)

        trajectories: list[Trajectory] = []

        for identifier in unique_ids:
            expression = QgsExpression(f'"{self.__id_field}" = {identifier}')
            request = QgsFeatureRequest(expression)

            order_clause = QgsFeatureRequest.OrderByClause(self.__timestamp_field, ascending=True)
            order_by = QgsFeatureRequest.OrderBy([order_clause])

            request.setOrderBy(order_by)

            features: QgsFeatureIterator = self.__layer.getFeatures(request)

            nodes: list[TrajectoryNode] = []

            for feature in features:
                point: QgsPointXY = feature.geometry().asPoint()
                timestamp: float = feature[timestamp_field_idx]
                width: int = feature[width_field_idx]
                length: int = feature[length_field_idx]
                height: int = feature[height_field_idx]

                if self.__timestamp_units == QgsUnitTypes.TemporalUnit.TemporalMilliseconds:
                    timestamp = timestamp / 1000

                nodes.append(
                    TrajectoryNode(point, datetime.fromtimestamp(timestamp, tz=timezone.utc), width, length, height)
                )

            trajectories.append(Trajectory(tuple(nodes), self))

        self.__trajectories = tuple(trajectories)

    def as_line_layer(self) -> QgsVectorLayer | None:
        # TODO: can this be a memory layer?
        line_layer = QgsVectorLayer("LineString?crs=3067", "Line Layer", "memory")

        line_layer.startEditing()

        line_layer.addAttribute(QgsField("fid", QVariant.Int))
        line_layer.addAttribute(QgsField("average_speed", QVariant.Double))

        fields = line_layer.fields()

        for i, trajectory in enumerate(self.__trajectories):
            feature = QgsFeature(fields)

            feature.setAttributes([i, trajectory.average_speed()])
            feature.setGeometry(trajectory.as_geometry())

            line_layer.addFeature(feature)

        line_layer.commitChanges()

        return line_layer

    def is_valid(self) -> bool:
        is_layer_valid: bool = self.__layer.isValid()
        if not is_layer_valid:
            msg = "Layer is not valid."
            raise ValueError(msg)

        is_point_layer: bool = self.__layer.geometryType() == QgsWkbTypes.GeometryType.PointGeometry
        if not is_point_layer:
            msg = "Layer is not a point layer."
            raise ValueError(msg)

        has_features: bool = self.__layer.hasFeatures() == QgsFeatureSource.FeatureAvailability.FeaturesAvailable
        if not has_features:
            msg = "Layer has no features."
            raise ValueError(msg)

        id_field_exists: bool = self.__layer.fields().indexFromName(self.__id_field) != -1
        if not id_field_exists:
            msg = "Id field not found in the layer."
            raise ValueError(msg)

        timestamp_field_exists: bool = self.__layer.fields().indexFromName(self.__timestamp_field) != -1
        if not timestamp_field_exists:
            msg = "Timestamp field not found in the layer."
            raise ValueError(msg)

        width_field_exists: bool = self.__layer.fields().indexFromName(self.__width_field) != -1
        if not width_field_exists:
            msg = "Width field not found in the layer."
            raise ValueError(msg)

        length_field_exists: bool = self.__layer.fields().indexFromName(self.__length_field) != -1
        if not length_field_exists:
            msg = "Length field not found in the layer."
            raise ValueError(msg)

        height_field_exists: bool = self.__layer.fields().indexFromName(self.__height_field) != -1
        if not height_field_exists:
            msg = "Height field not found in the layer."
            raise ValueError(msg)

        return True
