import pytest
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY

from fvh3t.core.exceptions import InvalidLayerException
from fvh3t.core.gate_layer import GateLayer
from fvh3t.core.line_layer import create_line_layer


def test_gate_layer_create_gates(qgis_gate_line_layer):
    gate_layer = GateLayer(
        qgis_gate_line_layer,
        "counts_left",
        "counts_right",
    )

    gates = gate_layer.gates()

    assert len(gates) == 3

    gate1 = gates[0]
    gate2 = gates[1]
    gate3 = gates[2]

    assert gate1.geometry().asWkt() == "LineString (0 0, 0 1, 0 2)"
    assert gate2.geometry().asWkt() == "LineString (5 5, 10 10)"
    assert gate3.geometry().asWkt() == "LineString (0.25 1, 1 1, 1.5 0.5, 1.5 0, 1 -0.5)"

    assert gate1.counts_left()
    assert gate1.counts_right()

    assert not gate2.counts_left()
    assert gate2.counts_right()

    assert gate3.counts_left()
    assert not gate3.counts_right()

    assert len(gate1.segments()) == 2
    assert len(gate2.segments()) == 1
    assert len(gate3.segments()) == 4


def test_is_field_valid(qgis_gate_line_layer, qgis_gate_line_layer_wrong_field_type):
    with pytest.raises(InvalidLayerException, match="Counts left field either not found or of incorrect type."):
        GateLayer(
            qgis_gate_line_layer,
            "count_right",  # use wrong field names on purpose
            "count_left",
        )

    with pytest.raises(InvalidLayerException, match="Counts right field either not found or of incorrect type."):
        GateLayer(
            qgis_gate_line_layer_wrong_field_type,
            "counts_left",
            "counts_right",
        )


def test_create_valid_gate_from_empty_line_layer():
    layer = create_line_layer()

    layer.startEditing()

    gate = QgsFeature(layer.fields())
    gate.setAttributes([True, True])
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
        "counts_left",
        "counts_right",
    )

    gates = gate_layer.gates()

    assert len(gates) == 1

    gate = gates[0]

    assert gate.geometry().asWkt() == "LineString (0 0, 0 1)"
    assert gate.counts_left()
    assert gate.counts_right()
    assert len(gate.segments()) == 1
