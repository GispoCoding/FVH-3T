from __future__ import annotations

from qgis.core import QgsFeatureSource, QgsField, QgsVectorLayer, QgsWkbTypes
from qgis.PyQt.QtCore import QMetaType

from fvh3t.core.exceptions import InvalidLayerException
from fvh3t.core.gate import Gate


class GateLayer:
    """
    Wrapper around a QgsVectorLayer object from which gates
    can be instantiated, i.e.

    1. is a line layer
    2. has a valid "counts left" field
    2. has a valid "counts right" field
    """

    def __init__(
        self,
        layer: QgsVectorLayer,
        counts_left_field: str,
        counts_right_field: str,
    ) -> None:
        self.__layer: QgsVectorLayer = layer
        self.__counts_left_field = counts_left_field
        self.__counts_right_field = counts_right_field

        if self.is_valid():
            self.__gates: tuple[Gate, ...] = ()
            self.create_gates()

    def create_gates(self) -> None:
        counts_left_field_idx: int = self.__layer.fields().indexOf(self.__counts_left_field)
        counts_right_field_idx: int = self.__layer.fields().indexOf(self.__counts_right_field)

        # TODO: Check that these are bool fields

        gates: list[Gate] = []

        for feature in self.__layer.getFeatures():
            counts_left: bool = feature[counts_left_field_idx]
            counts_right: bool = feature[counts_right_field_idx]

            gate = Gate(feature.geometry(), counts_left=counts_left, counts_right=counts_right)

            gates.append(gate)

        self.__gates = tuple(gates)

    def gates(self) -> tuple[Gate, ...]:
        return self.__gates

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

        if not self.is_field_valid(self.__counts_left_field, accepted_types=[QMetaType.Type.Bool]):
            msg = "Counts left field either not found or of incorrect type."
            raise InvalidLayerException(msg)

        if not self.is_field_valid(self.__counts_right_field, accepted_types=[QMetaType.Type.Bool]):
            msg = "Counts right field either not found or of incorrect type."
            raise InvalidLayerException(msg)

        return True
