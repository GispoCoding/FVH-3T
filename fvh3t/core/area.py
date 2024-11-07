from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import timedelta

    from fvh3t.core.trajectory import Trajectory, TrajectoryNode
    from fvh3t.core.trajectory_layer import TrajectoryLayer
    from fvh3t.core.trajectory_segment import TrajectorySegment

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsDistanceArea,
    QgsGeometry,
    QgsUnitTypes,
    QgsWkbTypes,
)

from fvh3t.core.exceptions import InvalidGeometryTypeException


class Area:
    """
    A wrapper class around a QgsGeometry which represents a
    polygon through which trajectories can pass. The geometry
    must be a polygon.
    """

    def __init__(
        self,
        geom: QgsGeometry,
        name: str,
    ) -> None:
        if geom.type() != QgsWkbTypes.GeometryType.PolygonGeometry:
            msg = "Area must be created from a polygon geometry!"
            raise InvalidGeometryTypeException(msg)

        self.__geom: QgsGeometry = geom
        self.__name: str = name
        self.__trajectory_count: int = 0
        self.__average_speed: float = 0.0

    def geometry(self) -> QgsGeometry:
        return self.__geom

    def name(self) -> str:
        return self.__name

    def trajectory_count(self) -> int:
        return self.__trajectory_count

    def average_speed(self) -> float:
        return self.__average_speed

    def intersects_trajectory(self, traj: Trajectory) -> bool:
        return self.__geom.intersects(traj.as_geometry())

    def get_inside_trajectories(self, trajectories: tuple[Trajectory, ...]) -> list[list[TrajectorySegment]]:
        inside_trajectories = []  # List to hold all (cut) trajectories that pass through a polygon
        for trajectory in trajectories:
            if self.intersects_trajectory(trajectory):
                inside_segments = []  # List to hold trajectory segments inside polygon on one trajectory
                traj_segments: tuple[TrajectorySegment, ...] = trajectory.as_segments()
                for i in range(len(traj_segments)):
                    traj_seg: TrajectorySegment = traj_segments[i]
                    # Take all segments in which at least one of the nodes is inside polygon
                    if not self.__geom.contains(traj_seg.node_a) and not self.__geom.contains(traj_seg.node_b):
                        continue
                    inside_segments.append(traj_seg)
                inside_trajectories.append(inside_segments)
        self.__trajectory_count = len(inside_trajectories)
        return inside_trajectories

    def compute_average_speed(
        self, trajectories: tuple[Trajectory, ...], trajectory_layer: TrajectoryLayer | None = None
    ) -> None:
        inside_trajectories = self.get_inside_trajectories(trajectories)
        da = QgsDistanceArea()

        crs = trajectory_layer.crs() if trajectory_layer else QgsCoordinateReferenceSystem("EPSG:3067")
        da.setSourceCrs(crs, QgsCoordinateTransformContext)

        convert: bool = da.lengthUnits() != QgsUnitTypes.DistanceUnit.DistanceMeters
        total_avg_speed_s = 0.0
        for trajectory_segments in inside_trajectories:
            total_speed_s = 0.0
            for traj_seg in trajectory_segments:
                current_node: TrajectoryNode = traj_seg.node_b
                previous_node: TrajectoryNode = traj_seg.node_a

                distance_m: float = da.measureLine(current_node.point, previous_node.point)
                if convert:
                    distance_m = da.convertLengthMeasurement(distance_m, QgsUnitTypes.DistanceUnit.DistanceMeters)

                time_difference: timedelta = current_node.timestamp - previous_node.timestamp
                speed_s: float = distance_m / time_difference.total_seconds()

                total_speed_s += speed_s
            avg_speed_s = total_speed_s / len(trajectory_segments)
            total_avg_speed_s += avg_speed_s
        self.__average_speed = total_avg_speed_s / len(inside_trajectories)
