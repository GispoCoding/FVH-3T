from __future__ import annotations

from qgis.core import QgsFeature, QgsFeatureSource, QgsField, QgsVectorLayer, QgsWkbTypes
from qgis.PyQt.QtCore import QDateTime, QMetaType, QVariant

from fvh3t.core.exceptions import InvalidFeatureException, InvalidLayerException
from fvh3t.core.gate import Gate


class GateLayer:
    """
    Wrapper around a QgsVectorLayer object from which gates
    can be instantiated, i.e.

    1. is a line layer
    2. has a valid "counts negative" field
    2. has a valid "counts positive" field
    """

    def __init__(
        self,
        layer: QgsVectorLayer,
        name_field: str,
        counts_negative_field: str,
        counts_positive_field: str,
    ) -> None:
        self.__layer: QgsVectorLayer = layer
        self.__name_field = name_field
        self.__counts_negative_field = counts_negative_field
        self.__counts_positive_field = counts_positive_field

        if self.is_valid():
            self.__gates: tuple[Gate, ...] = ()
            self.create_gates()

    def create_gates(self) -> None:
        name_field_idx: int = self.__layer.fields().indexOf(self.__name_field)
        counts_negative_field_idx: int = self.__layer.fields().indexOf(self.__counts_negative_field)
        counts_positive_field_idx: int = self.__layer.fields().indexOf(self.__counts_positive_field)

        gates: list[Gate] = []

        for feature in self.__layer.getFeatures():
            name: str = feature[name_field_idx]
            counts_negative: bool = feature[counts_negative_field_idx]
            counts_positive: bool = feature[counts_positive_field_idx]

            gate = Gate(
                feature.geometry(),
                name=name,
                counts_negative=counts_negative,
                counts_positive=counts_positive,
            )

            gates.append(gate)

        self.__gates = tuple(gates)

    def gates(self) -> tuple[Gate, ...]:
        return self.__gates

    def as_line_layer(self, traveler_class: str, start_time: QDateTime, end_time: QDateTime) -> QgsVectorLayer | None:
        line_layer = QgsVectorLayer("LineString?crs=3067", "Line Layer", "memory")

        line_layer.startEditing()

        line_layer.addAttribute(QgsField("fid", QVariant.Int))
        line_layer.addAttribute(QgsField("name", QVariant.String))
        line_layer.addAttribute(QgsField("traveler_class", QVariant.String))
        line_layer.addAttribute(QgsField("start_time", QVariant.Time))
        line_layer.addAttribute(QgsField("end_time", QVariant.Time))
        line_layer.addAttribute(QgsField("counts_negative", QVariant.Bool))
        line_layer.addAttribute(QgsField("counts_positive", QVariant.Bool))
        line_layer.addAttribute(QgsField("trajectory_count", QVariant.Int))
        line_layer.addAttribute(QgsField("average_speed (km/h)", QVariant.Double))
        line_layer.addAttribute(QgsField("average_acceleration (m/s²)", QVariant.Double))

        fields = line_layer.fields()

        for i, gate in enumerate(self.__gates):
            feature = QgsFeature(fields)

            feature.setAttributes(
                [
                    i,
                    gate.name(),
                    traveler_class,
                    start_time,
                    end_time,
                    gate.counts_negative(),
                    gate.counts_positive(),
                    gate.trajectory_count(),
                    gate.average_speed(),
                    gate.average_acceleration(),
                ]
            )
            feature.setGeometry(gate.geometry())

            if not feature.isValid():
                raise InvalidFeatureException

            line_layer.addFeature(feature)

        line_layer.commitChanges()

        return line_layer

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

        is_line_layer: bool = self.__layer.geometryType() == QgsWkbTypes.GeometryType.LineGeometry
        if not is_line_layer:
            msg = "Layer is not a line layer."
            raise InvalidLayerException(msg)

        has_features: bool = self.__layer.hasFeatures() == QgsFeatureSource.FeatureAvailability.FeaturesAvailable
        if not has_features:
            msg = "Layer has no features."
            raise InvalidLayerException(msg)

        if not self.is_field_valid(self.__name_field, accepted_types=[QMetaType.Type.QString]):
            msg = "Name field either not found or of incorrect type."
            raise InvalidLayerException(msg)

        if not self.is_field_valid(self.__counts_negative_field, accepted_types=[QMetaType.Type.Bool]):
            msg = "Counts negative field either not found or of incorrect type."
            raise InvalidLayerException(msg)

        if not self.is_field_valid(self.__counts_positive_field, accepted_types=[QMetaType.Type.Bool]):
            msg = "Counts positive field either not found or of incorrect type."
            raise InvalidLayerException(msg)

        return True
