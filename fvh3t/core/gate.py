from qgis.core import QgsGeometry

class Gate:

    def __init__(self, geom: QgsGeometry) -> None:
        self.__geom: QgsGeometry = geom

    def geometry(self) -> QgsGeometry:
        return self.__geom

