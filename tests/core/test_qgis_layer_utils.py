from qgis.core import QgsCoordinateReferenceSystem

from fvh3t.core.qgis_layer_utils import QgisLayerUtils


def test_create_gate_layer():
    crs = QgsCoordinateReferenceSystem("EPSG:3067")

    layer = QgisLayerUtils.create_gate_layer(crs)

    assert layer.name() == "Gate Layer"

    fields = layer.fields()

    assert len(fields) == 3

    assert fields[0].name() == "name"
    assert fields[1].name() == "counts_negative"
    assert fields[2].name() == "counts_positive"

    assert fields[0].typeName() == "string"
    assert fields[1].typeName() == "boolean"
    assert fields[2].typeName() == "boolean"

    assert layer.constraintExpression(1) == '"counts_negative" OR "counts_positive"'
    assert layer.constraintExpression(2) == '"counts_negative" OR "counts_positive"'
