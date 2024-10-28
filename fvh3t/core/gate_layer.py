from __future__ import annotations

from qgis.core import QgsFeatureSource, QgsVectorLayer, QgsWkbTypes

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

        if not self.is_valid():
            msg = "GateLayer could not be properly created!"
            raise InvalidLayerException(msg)

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

    def is_valid(self) -> bool:
        is_layer_valid: bool = self.__layer.isValid()
        if not is_layer_valid:
            msg = "Layer is not valid."
            raise ValueError(msg)

        is_point_layer: bool = self.__layer.geometryType() == QgsWkbTypes.GeometryType.LineGeometry
        if not is_point_layer:
            msg = "Layer is not a point layer."
            raise ValueError(msg)

        has_features: bool = self.__layer.hasFeatures() == QgsFeatureSource.FeatureAvailability.FeaturesAvailable
        if not has_features:
            msg = "Layer has no features."
            raise ValueError(msg)

        counts_left_field_exists: bool = self.__layer.fields().indexFromName(self.__counts_left_field) != -1
        if not counts_left_field_exists:
            msg = "Counts left field not found in the layer."
            raise ValueError(msg)

        counts_right_field_exists: bool = self.__layer.fields().indexFromName(self.__counts_right_field) != -1
        if not counts_right_field_exists:
            msg = "Counts right field not found in the layer."
            raise ValueError(msg)

        return True
