from qgis.core import QgsGeometry


class Gate:
    """
    A wrapper class around a QgsGeometry which represents a
    gate through which trajectories can pass. The geometry
    must be a line.
    """

    def __init__(self, geom: QgsGeometry) -> None:
        self.__geom: QgsGeometry = geom

    def geometry(self) -> QgsGeometry:
        return self.__geom
