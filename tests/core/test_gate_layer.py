from fvh3t.core.gate_layer import GateLayer


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
