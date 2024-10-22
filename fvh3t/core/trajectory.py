from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple

from qgis.core import (
    QgsExpression,
    QgsFeature,
    QgsFeatureIterator,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

if TYPE_CHECKING:
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

    def nodes(self) -> tuple[TrajectoryNode, ...]:
        return self.__nodes

    def as_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPolylineXY([node.point for node in self.__nodes])

    def intersects_gate(self, other: Gate) -> bool:
        return self.as_geometry().intersects(other.geometry())

    def _movement_core(self) -> tuple[float, int, float]:
        total_distance = 0.0
        total_time = 0
        max_speed = 0.0
        nodes = self.nodes()
        for i in range(1, len(nodes)):
            current_node = nodes[i]
            previous_node = nodes[i - 1]

            distance = current_node.point.distance(previous_node.point)
            time_difference = current_node.timestamp - previous_node.timestamp
            speed = distance / time_difference
            if speed > max_speed:
                max_speed = speed

            total_distance += distance
            total_time += time_difference

        return total_distance, total_time, max_speed

    def maximum_speed(self) -> float:
        _, _, max_speed = self._movement_core()
        return round(max_speed, 2)

    def average_speed(self) -> float:
        total_distance, total_time, _ = self._movement_core()
        if total_time > 0:
            return round(total_distance / total_time, 2)

        return 0.0

    def length(self) -> float:
        length, _, _ = self._movement_core()
        return round(length, 2)

    def duration(self) -> int:
        _, duration, _ = self._movement_core()
        return duration


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

        # TODO: should the class of traveler be handled here?

        self.__trajectories: tuple[Trajectory, ...] = ()

    def layer(self) -> QgsVectorLayer:
        return self.__layer

    def id_field(self) -> str:
        return self.__id_field

    def timestamp_field(self) -> str:
        return self.__timestamp_field

    def trajectories(self) -> tuple[Trajectory, ...]:
        return self.__trajectories

    def create_trajectories(self) -> None:
        if not self.is_valid():
            return

        id_field_idx: int = self.__layer.fields().indexOf(self.__id_field)
        timestamp_field_idx: int = self.__layer.fields().indexOf(self.__timestamp_field)

        unique_ids: set[Any] = self.__layer.uniqueValues(id_field_idx)

        trajectories: list[Trajectory] = []

        for identifier in unique_ids:
            expression = QgsExpression(f'"{self.__id_field}" = {identifier}')
            request = QgsFeatureRequest(expression)

            order_clause = QgsFeatureRequest.OrderByClause(self.__timestamp_field, ascending=True)
            order_by = QgsFeatureRequest.OrderBy([order_clause])

            request.setOrderBy(order_by)

            features: QgsFeatureIterator = self.__layer.getFeatures(request)

            nodes: list[TrajectoryNode] = []

            for feature in features:
                point: QgsPointXY = feature.geometry().asPoint()
                timestamp: int = feature[timestamp_field_idx]

                nodes.append(TrajectoryNode(point, timestamp))

            trajectories.append(Trajectory(tuple(nodes)))

        self.__trajectories = tuple(trajectories)

    def as_line_layer(self) -> QgsVectorLayer | None:
        if not self.is_valid():
            return None

        # TODO: can this be a memory layer?
        line_layer = QgsVectorLayer("LineString?crs=3067", "Line Layer", "memory")

        line_layer.startEditing()

        line_layer.addAttribute(QgsField("fid", QVariant.Int))
        line_layer.addAttribute(QgsField("average_speed", QVariant.Double))

        fields = line_layer.fields()

        for i, trajectory in enumerate(self.__trajectories):
            feature = QgsFeature(fields)

            feature.setAttributes([i, trajectory.average_speed()])
            feature.setGeometry(trajectory.as_geometry())

            line_layer.addFeature(feature)

        line_layer.commitChanges()

        return line_layer

    def is_valid(self) -> bool:
        is_point_layer: bool = self.__layer.geometryType() == QgsWkbTypes.GeometryType.PointGeometry
        id_field_exists: bool = self.__layer.fields().indexFromName(self.__id_field) != -1
        timestamp_field_exists: bool = self.__layer.fields().indexFromName(self.__timestamp_field) != -1

        return is_point_layer and id_field_exists and timestamp_field_exists
