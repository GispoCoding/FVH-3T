import math

from typing import NamedTuple

from qgis.core import QgsGeometry, QgsPointXY, QgsVectorLayer, QgsWkbTypes

from fvh3t.core.gate import Gate


class TrajectoryNode(NamedTuple):
    """
    A simple data container representing one node in a
    trajectory.
    """

    point: QgsPointXY
    timestamp: int

    @classmethod
    def from_coordinates(cls, x: float, y: float, timestamp: int):
        return cls(QgsPointXY(x, y), timestamp)


class Trajectory:
    """
    Class representing a trajectory which consists
    of nodes which have a location and a timestamp
    """

    def __init__(self, nodes: tuple[TrajectoryNode, ...]) -> None:
        self.__nodes: tuple[TrajectoryNode, ...] = nodes

    def as_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPolylineXY([node.point for node in self.__nodes])

    def intersects_gate(self, other: Gate) -> bool:
        return self.as_geometry().intersects(other.geometry())

    def average_speed(self) -> float:
        total_distance = 0.0
        total_time = 0
        for i in range(1, len(self.__nodes)):
            current_node = self.__nodes[i]
            previous_node = self.__nodes[i - 1]

            distance = math.sqrt(
                (current_node.point.x - previous_node.point.x) ** 2
                + (current_node.point.y - previous_node.point.y) ** 2
            )

            time_difference = current_node.timestamp - previous_node.timestamp

            total_distance += distance
            total_time += time_difference

        if total_time > 0:
            return total_distance / total_time

        else:
            return 0.0


class TrajectoryLayer:
    """
    Wrapper around a QgsVectorLayer object from which trajectories
    can be instantiated, i.e.

    1. is a point layer
    2. has a valid identifier field
    3. has a valid timestamp field
    """

    def __init__(self, layer: QgsVectorLayer, id_field: str, timestamp_field: str) -> None:
        self.__layer: QgsVectorLayer = layer
        self.__id_field: str = id_field
        self.__timestamp_field: str = timestamp_field

    def is_valid(self) -> bool:
        is_point_layer: bool = self.__layer.geometryType() == QgsWkbTypes.GeometryType.PointGeometry
        id_field_exists: bool = self.__layer.fields().indexFromName(self.__id_field) != -1
        timestamp_field_exists: bool = self.__layer.fields().indexFromName(self.__timestamp_field) != -1

        return is_point_layer and id_field_exists and timestamp_field_exists
