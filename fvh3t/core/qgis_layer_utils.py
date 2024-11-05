from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeatureRenderer,
    QgsField,
    QgsFieldConstraints,
    QgsReadWriteContext,
    QgsVectorLayer,
    edit,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtXml import QDomDocument

from fvh3t.qgis_plugin_tools.tools.resources import resources_path


class QgisLayerUtils:
    @staticmethod
    def set_gate_style(layer: QgsVectorLayer) -> None:
        doc = QDomDocument()

        with open(resources_path("style", "gate_style.xml")) as style_file:
            doc.setContent(style_file.read())

        renderer = QgsFeatureRenderer.load(doc.documentElement(), QgsReadWriteContext())
        layer.setRenderer(renderer)

    @staticmethod
    def create_gate_layer(crs: QgsCoordinateReferenceSystem) -> QgsVectorLayer:
        layer = QgsVectorLayer("LineString", "Gate Layer", "memory")
        layer.setCrs(crs)

        with edit(layer):
            layer.addAttribute(QgsField("name", QVariant.String))
            layer.addAttribute(QgsField("counts_negative", QVariant.Bool))
            layer.addAttribute(QgsField("counts_positive", QVariant.Bool))

        layer.setFieldConstraint(1, QgsFieldConstraints.ConstraintExpression)
        layer.setConstraintExpression(1, '"counts_negative" OR "counts_positive"')

        layer.setFieldConstraint(2, QgsFieldConstraints.ConstraintExpression)
        layer.setConstraintExpression(2, '"counts_negative" OR "counts_positive"')

        QgisLayerUtils.set_gate_style(layer)

        return layer
