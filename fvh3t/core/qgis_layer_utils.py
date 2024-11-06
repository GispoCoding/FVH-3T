from qgis.core import QgsFeatureRenderer, QgsReadWriteContext, QgsVectorLayer
from qgis.PyQt.QtXml import QDomDocument

from fvh3t.qgis_plugin_tools.tools.resources import resources_path


class QgisLayerUtils:
    @staticmethod
    def set_gate_style(layer: QgsVectorLayer):
        doc = QDomDocument()

        with open(resources_path("style", "gate_style.xml")) as style_file:
            doc.setContent(style_file.read())

        renderer = QgsFeatureRenderer.load(doc.documentElement(), QgsReadWriteContext())
        layer.setRenderer(renderer)
