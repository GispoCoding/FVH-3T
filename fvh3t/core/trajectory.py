from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, NamedTuple

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsUnitTypes,
)

from fvh3t.core.exceptions import InvalidTrajectoryException
from fvh3t.core.trajectory_segment import TrajectorySegment

if TYPE_CHECKING:
    from fvh3t.core.trajectory_layer import TrajectoryLayer

N_NODES_MIN = 2


class TrajectoryNode(NamedTuple):
    """
    A simple data container representing one node in a
    trajectory.
    """

    point: QgsPointXY
    timestamp: datetime
    width: float
    length: float
    height: float

    @classmethod
    def from_coordinates(
        cls,
        x: float,
        y: float,
        timestamp: float,
        width: float,
        length: float,
        height: float,
        *,
        timestamp_in_ms: bool = True,
    ):
        if timestamp_in_ms:
            timestamp = timestamp / 1000

        return cls(QgsPointXY(x, y), datetime.fromtimestamp(timestamp, tz=timezone.utc), width, length, height)


class Trajectory:
    """
    Class representing a trajectory which consists
    of nodes which have a location, size (width, length, height),
    and a timestamp
    """

    def __init__(self, nodes: tuple[TrajectoryNode, ...], layer: TrajectoryLayer | None = None) -> None:
        if len(nodes) < N_NODES_MIN:
            msg = "Trajectory must consist of at least two nodes."
            raise InvalidTrajectoryException(msg)

        self.__nodes: tuple[TrajectoryNode, ...] = nodes
        self.__layer: TrajectoryLayer | None = layer

    def nodes(self) -> tuple[TrajectoryNode, ...]:
        return self.__nodes

    def as_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPolylineXY([node.point for node in self.__nodes])

    def as_segments(self) -> tuple[TrajectorySegment, ...]:
        segments: list[TrajectorySegment] = []
        for i in range(1, len(self.__nodes)):
            previous_node: TrajectoryNode = self.__nodes[i - 1]
            current_node: TrajectoryNode = self.__nodes[i]

            segments.append(TrajectorySegment(previous_node, current_node))

        return tuple(segments)

    def _movement_core(self) -> tuple[float, timedelta, float]:
        total_distance_m = 0.0
        total_time_s = timedelta(0)
        max_speed_m_per_s = 0.0

        da = QgsDistanceArea()

        if self.__layer is not None:
            da.setSourceCrs(self.__layer.crs(), QgsCoordinateTransformContext())
        else:
            da.setSourceCrs(QgsCoordinateReferenceSystem("EPSG:3067"), QgsCoordinateTransformContext())

        convert: bool = da.lengthUnits() != QgsUnitTypes.DistanceUnit.DistanceMeters

        for i in range(1, len(self.__nodes)):
            current_node: TrajectoryNode = self.__nodes[i]
            previous_node: TrajectoryNode = self.__nodes[i - 1]

            distance_m: float = da.measureLine(current_node.point, previous_node.point)
            if convert:
                distance_m = da.convertLengthMeasurement(distance_m, QgsUnitTypes.DistanceUnit.DistanceMeters)

            time_difference: timedelta = current_node.timestamp - previous_node.timestamp
            speed_s: float = distance_m / time_difference.total_seconds()

            if speed_s > max_speed_m_per_s:
                max_speed_m_per_s = speed_s

            total_distance_m += distance_m
            total_time_s += time_difference

        return total_distance_m, total_time_s, max_speed_m_per_s

    def maximum_speed(self) -> float:
        # here the max speed is in meters / second
        # convert to km/h
        _, _, max_speed = self._movement_core()

        max_speed = max_speed * 3.6
        return round(max_speed, 2)

    def average_speed(self) -> float:
        total_distance_m, total_time_s, _ = self._movement_core()
        seconds: float = total_time_s.total_seconds()

        # calculate m/s
        if seconds > 0:
            meters_per_second = total_distance_m / seconds

            # calculate and return in km/h
            return round(meters_per_second * 3.6, 2)

        return 0.0

    def length(self) -> float:
        length, _, _ = self._movement_core()
        return round(length, 2)

    def duration(self) -> timedelta:
        _, duration, _ = self._movement_core()
        return duration

    def minimum_size(self) -> tuple[float, float, float]:
        nodes = self.nodes()
        min_width, min_length, min_height = (
            min((node.width for node in nodes), default=0.0),
            min((node.length for node in nodes), default=0.0),
            min((node.height for node in nodes), default=0.0),
        )

        return round(min_width, 2), round(min_length, 2), round(min_height, 2)

    def maximum_size(self) -> tuple[float, float, float]:
        nodes = self.nodes()
        max_width, max_length, max_height = (
            max((node.width for node in nodes), default=0.0),
            max((node.length for node in nodes), default=0.0),
            max((node.height for node in nodes), default=0.0),
        )

        return round(max_width, 2), round(max_length, 2), round(max_height, 2)

    def average_size(self) -> tuple[float, float, float]:
        nodes = self.nodes()
        n_nodes = len(nodes)
        if n_nodes == 0:
            return 0.0, 0.0, 0.0

        total_width, total_length, total_height = (
            sum(node.width for node in nodes),
            sum(node.length for node in nodes),
            sum(node.height for node in nodes),
        )

        return round(total_width / n_nodes, 2), round(total_length / n_nodes, 2), round(total_height / n_nodes, 2)
