from __future__ import annotations

from math import log10
from typing import TYPE_CHECKING, Any, NamedTuple

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsDistanceArea,
    QgsExpression,
    QgsFeature,
    QgsFeatureIterator,
    QgsFeatureRequest,
    QgsFeatureSource,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

if TYPE_CHECKING:
    from fvh3t.core.gate import Gate


UNIX_TIMESTAMP_UNIT_THRESHOLD = 13


def digits_in_timestamp_int(num: int):
    return int(log10(num)) + 1


class TrajectoryNode(NamedTuple):
    """
    A simple data container representing one node in a
    trajectory.
    """

    point: QgsPointXY
    timestamp: int
    width: float
    length: float
    height: float

    @classmethod
    def from_coordinates(cls, x: float, y: float, timestamp: int, width: float, length: float, height: float):
        return cls(QgsPointXY(x, y), timestamp, width, length, height)


class Trajectory:
    """
    Class representing a trajectory which consists
    of nodes which have a location, size (width, length, height),
    and a timestamp
    """

    def __init__(self, nodes: tuple[TrajectoryNode, ...], layer: TrajectoryLayer | None = None) -> None:
        self.__nodes: tuple[TrajectoryNode, ...] = nodes
        self.__layer: TrajectoryLayer | None = layer

    def nodes(self) -> tuple[TrajectoryNode, ...]:
        return self.__nodes

    def as_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPolylineXY([node.point for node in self.__nodes])

    def intersects_gate(self, other: Gate) -> bool:
        return self.as_geometry().intersects(other.geometry())

    def _movement_core(self) -> tuple[float, int, float]:
        total_distance = 0.0
        total_time = 0
        max_speed = 0.0

        da = QgsDistanceArea()

        if self.__layer is not None:
            da.setSourceCrs(self.__layer.crs(), QgsCoordinateTransformContext())
        else:
            da.setSourceCrs(QgsCoordinateReferenceSystem("EPSG:3067"), QgsCoordinateTransformContext())

        convert: bool = da.lengthUnits() != QgsUnitTypes.DistanceUnit.DistanceMeters

        for i in range(1, len(self.__nodes)):
            current_node = self.__nodes[i]
            previous_node = self.__nodes[i - 1]

            distance = da.measureLine(current_node.point, previous_node.point)
            if convert:
                distance = da.convertLengthMeasurement(distance, QgsUnitTypes.DistanceUnit.DistanceMeters)

            time_difference = current_node.timestamp - previous_node.timestamp
            speed = distance / time_difference

            if speed > max_speed:
                max_speed = speed

            total_distance += distance
            total_time += time_difference

        return total_distance, total_time, max_speed

    def maximum_speed(self) -> float:
        # here the max speed is in meters / millisecond
        # convert to km/h
        _, _, max_speed = self._movement_core()

        max_speed = max_speed * 3600
        return round(max_speed, 2)

    def average_speed(self) -> float:
        total_distance, total_time, _ = self._movement_core()

        # here the distance should've already been converted
        # to meters and the time is in milliseconds
        # convert to kilometers and hours respectively
        total_distance_km: float = total_distance / 1000
        total_time_h: float = ((total_time / 1000) / 60) / 60

        if total_time_h > 0:
            return round((total_distance_km / total_time_h), 2)

        return 0.0

    def length(self) -> float:
        length, _, _ = self._movement_core()
        return round(length, 2)

    def duration(self) -> int:
        _, duration, _ = self._movement_core()
        return duration

    def minimum_size(self) -> tuple[float, float, float]:
        nodes = self.nodes()
        min_width, min_length, min_height = (
            min((node.width for node in nodes), default=0.0),
            min((node.length for node in nodes), default=0.0),
            min((node.height for node in nodes), default=0.0),
        )

        return round(min_width, 2), round(min_length, 2), round(min_height, 2)

    def maximum_size(self) -> tuple[float, float, float]:
        nodes = self.nodes()
        max_width, max_length, max_height = (
            max((node.width for node in nodes), default=0.0),
            max((node.length for node in nodes), default=0.0),
            max((node.height for node in nodes), default=0.0),
        )

        return round(max_width, 2), round(max_length, 2), round(max_height, 2)

    def average_size(self) -> tuple[float, float, float]:
        nodes = self.nodes()
        n_nodes = len(nodes)
        if n_nodes == 0:
            return 0.0, 0.0, 0.0

        total_width, total_length, total_height = (
            sum(node.width for node in nodes),
            sum(node.length for node in nodes),
            sum(node.height for node in nodes),
        )

        return round(total_width / n_nodes, 2), round(total_length / n_nodes, 2), round(total_height / n_nodes, 2)


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

        self.__trajectories: tuple[Trajectory, ...] = ()

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
        if not self.is_valid():
            return

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
                timestamp: int = feature[timestamp_field_idx]
                width: int = feature[width_field_idx]
                length: int = feature[length_field_idx]
                height: int = feature[height_field_idx]

                if self.__timestamp_units == QgsUnitTypes.TemporalUnit.TemporalSeconds:
                    # TODO: this means we're storing timestamps as milliseconds
                    # We might want to use datetime or maybe convert to seconds?
                    timestamp = timestamp * 1000

                nodes.append(TrajectoryNode(point, timestamp, width, length, height))

            trajectories.append(Trajectory(tuple(nodes), self))

        self.__trajectories = tuple(trajectories)

    def as_line_layer(self) -> QgsVectorLayer | None:
        if not self.is_valid():
            return None

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
