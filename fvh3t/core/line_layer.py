from __future__ import annotations

from qgis.core import QgsField, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant


# TODO: Tässä ei tarvii muuta kuin luoda tyhjä viivataso. Lisäksi, lisää style (katso issue!)
def create_line_layer() -> QgsVectorLayer:
    layer = QgsVectorLayer("LineString?crs=EPSG:3067", "Line Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("counts_left", QVariant.Bool))
    layer.addAttribute(QgsField("counts_right", QVariant.Bool))

    layer.commitChanges()

    return layer
