from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fvh3t.core.trajectory import Trajectory
    from fvh3t.core.trajectory_layer import TrajectoryLayer

from qgis.core import (
    QgsGeometry,
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

    def intersects(self, traj: Trajectory) -> bool:
        return self.__geom.intersects(traj.as_geometry())

    def count_trajectories_from_layer(self, layer: TrajectoryLayer) -> None:
        self.count_trajectories(layer.trajectories())

    def count_trajectories(
        self,
        trajectories: tuple[Trajectory, ...],
    ) -> None:
        speed = 0.0

        for trajectory in trajectories:
            if self.intersects(trajectory):
                traj_speed = trajectory.average_speed()
                speed += traj_speed

                self.__trajectory_count += 1

        if self.__trajectory_count > 0:
            self.__average_speed = speed / self.__trajectory_count
