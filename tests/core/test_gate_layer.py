import pytest
from qgis.core import QgsCoordinateReferenceSystem, QgsFeature, QgsGeometry, QgsPointXY

from fvh3t.core.exceptions import InvalidLayerException
from fvh3t.core.gate_layer import GateLayer
from fvh3t.core.qgis_layer_utils import QgisLayerUtils


def test_gate_layer_create_gates(qgis_gate_line_layer):
    gate_layer = GateLayer(
        qgis_gate_line_layer,
        "name",
        "counts_negative",
        "counts_positive",
    )

    gates = gate_layer.gates()

    assert len(gates) == 3

    gate1 = gates[0]
    gate2 = gates[1]
    gate3 = gates[2]

    assert gate1.geometry().asWkt() == "LineString (0 0, 0 1, 0 2)"
    assert gate2.geometry().asWkt() == "LineString (5 5, 10 10)"
    assert gate3.geometry().asWkt() == "LineString (0.25 1, 1 1, 1.5 0.5, 1.5 0, 1 -0.5)"

    assert gate1.counts_negative()
    assert gate1.counts_positive()

    assert not gate2.counts_negative()
    assert gate2.counts_positive()

    assert gate3.counts_negative()
    assert not gate3.counts_positive()

    assert len(gate1.segments()) == 2
    assert len(gate2.segments()) == 1
    assert len(gate3.segments()) == 4


def test_is_field_valid(qgis_gate_line_layer, qgis_gate_line_layer_wrong_field_type):
    with pytest.raises(InvalidLayerException, match="Counts negative field either not found or of incorrect type."):
        GateLayer(
            qgis_gate_line_layer,
            "name",
            "count_positive",  # use wrong field names on purpose
            "count_negative",
        )

    with pytest.raises(InvalidLayerException, match="Counts positive field either not found or of incorrect type."):
        GateLayer(
            qgis_gate_line_layer_wrong_field_type,
            "name",
            "counts_negative",
            "counts_positive",
        )


def test_create_valid_gate_from_empty_line_layer():
    layer = QgisLayerUtils.create_gate_layer(QgsCoordinateReferenceSystem("EPSG:3067"))

    layer.startEditing()

    gate = QgsFeature(layer.fields())
    gate.setAttributes(["name", True, True])
    gate.setGeometry(
        QgsGeometry.fromPolylineXY(
            [
                QgsPointXY(0, 0),
                QgsPointXY(0, 1),
            ]
        )
    )

    layer.addFeature(gate)

    layer.commitChanges()

    gate_layer = GateLayer(
        layer,
        "name",
        "counts_negative",
        "counts_positive",
    )

    gates = gate_layer.gates()

    assert len(gates) == 1

    gate = gates[0]

    assert gate.geometry().asWkt() == "LineString (0 0, 0 1)"
    assert gate.counts_negative()
    assert gate.counts_positive()
    assert len(gate.segments()) == 1
