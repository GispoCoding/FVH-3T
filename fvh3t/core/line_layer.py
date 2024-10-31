from __future__ import annotations

from qgis.core import QgsField, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant


def create_line_layer() -> QgsVectorLayer:
    layer = QgsVectorLayer("LineString?crs=EPSG:3067", "Line Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("counts_negative", QVariant.Bool))
    layer.addAttribute(QgsField("counts_positive", QVariant.Bool))

    layer.commitChanges()

    return layer
