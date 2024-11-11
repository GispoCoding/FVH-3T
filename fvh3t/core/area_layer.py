from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.core import QgsFeature, QgsFeatureSource, QgsField, QgsVectorLayer, QgsWkbTypes
from qgis.PyQt.QtCore import QDateTime, QMetaType, QVariant

from fvh3t.core.area import Area
from fvh3t.core.exceptions import InvalidFeatureException, InvalidLayerException

if TYPE_CHECKING:
    from fvh3t.core.trajectory_layer import TrajectoryLayer


class AreaLayer:
    """
    Wrapper around a QgsVectorLayer object from which areas
    can be instantiated, i.e.

    1. is a polygon layer
    2. has a name field
    3. has features
    """

    def __init__(
        self,
        layer: QgsVectorLayer,
        id_field: str,
        name_field: str,
    ) -> None:
        self.__layer: QgsVectorLayer = layer
        self.__name_field = name_field
        self.__id_field = id_field

        if self.is_valid():
            self.__areas: tuple[Area, ...] = ()
            self.create_areas()

    def create_areas(self) -> None:
        name_field_idx: int = self.__layer.fields().indexOf(self.__name_field)
        areas: list[Area] = []

        for feature in self.__layer.getFeatures():
            name: str = feature[name_field_idx]
            area = Area(
                feature.geometry(),
                name=name,
            )

            areas.append(area)

        self.__areas = tuple(areas)

    def count_trajectories_from_layer(self, layer: TrajectoryLayer) -> None:
        for area in self.__areas:
            area.count_trajectories_from_layer(layer)

    def areas(self) -> tuple[Area, ...]:
        return self.__areas

    def as_polygon_layer(
        self, traveler_class: str | None, start_time: QDateTime, end_time: QDateTime
    ) -> QgsVectorLayer | None:
        polygon_layer = QgsVectorLayer("Polygon", "Polygon Layer", "memory")
        polygon_layer.setCrs(self.__layer.crs())

        polygon_layer.startEditing()

        polygon_layer.addAttribute(QgsField("fid", QVariant.Int))
        polygon_layer.addAttribute(QgsField("name", QVariant.String))
        polygon_layer.addAttribute(QgsField("class", QVariant.String))
        polygon_layer.addAttribute(QgsField("interval_start", QVariant.DateTime))
        polygon_layer.addAttribute(QgsField("interval_end", QVariant.DateTime))
        polygon_layer.addAttribute(QgsField("vehicle_count", QVariant.Int))
        polygon_layer.addAttribute(QgsField("speed_avg (km/h)", QVariant.Double))

        fields = polygon_layer.fields()

        for i, area in enumerate(self.__areas, 1):
            feature = QgsFeature(fields)

            feature.setAttributes(
                [
                    i,
                    area.name(),
                    traveler_class if traveler_class else "all",
                    start_time,
                    end_time,
                    area.trajectory_count(),
                    round(area.average_speed(), 2),
                ]
            )
            feature.setGeometry(area.geometry())

            if not feature.isValid():
                raise InvalidFeatureException

            polygon_layer.addFeature(feature)

        polygon_layer.commitChanges()

        return polygon_layer

    def is_field_valid(self, field_name: str, *, accepted_types: list[QMetaType.Type]) -> bool:
        """
        Check that a field 1) exists and 2) has an
        acceptable type. Leave type list empty to
        allow any type.
        """
        field_id: int = self.__layer.fields().indexFromName(field_name)

        if field_id == -1:
            return False

        if not accepted_types:  # means all types are accepted
            return True

        field: QgsField = self.__layer.fields().field(field_id)
        field_type: QMetaType.Type = field.type()

        return field_type in accepted_types

    def is_valid(self) -> bool:
        is_layer_valid: bool = self.__layer.isValid()
        if not is_layer_valid:
            msg = "Layer is not valid."
            raise InvalidLayerException(msg)

        is_polygon_layer: bool = self.__layer.geometryType() == QgsWkbTypes.GeometryType.PolygonGeometry
        if not is_polygon_layer:
            msg = "Layer is not a polygon layer."
            raise InvalidLayerException(msg)

        has_features: bool = self.__layer.hasFeatures() == QgsFeatureSource.FeatureAvailability.FeaturesAvailable
        if not has_features:
            msg = "Layer has no features."
            raise InvalidLayerException(msg)

        if not self.is_field_valid(self.__name_field, accepted_types=[QMetaType.Type.QString]):
            msg = "Name field either not found or of incorrect type."
            raise InvalidLayerException(msg)

        if not self.is_field_valid(self.__id_field, accepted_types=[]):
            msg = "ID field not found."
            raise InvalidLayerException(msg)

        return True
