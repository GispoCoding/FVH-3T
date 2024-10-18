from typing import Tuple, NamedTuple

from qgis.core import QgsGeometry, QgsPointXY

class TrajectoryNode(NamedTuple):
    point: QgsPointXY
    timestamp: int

    @classmethod
    def from_coordinates(cls, x: float, y: float, timestamp: int):
        return cls(QgsPointXY(x, y), timestamp)


class Trajectory:

    def __init__(self, nodes: Tuple[TrajectoryNode]) -> None:
        self.__nodes: Tuple[TrajectoryNode] = nodes

    def as_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPolylineXY([node.point for node in self.__nodes])

    def intersects(self, other_geom: QgsGeometry) -> bool:
        return self.as_geometry().intersects(other_geom)

    def average_speed(self) -> float:
        # TODO: implement function
        return 0.0

