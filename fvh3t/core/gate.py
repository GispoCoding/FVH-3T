from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.core import QgsGeometry

    from fvh3t.core.trajectory import Trajectory, TrajectoryLayer


class Gate:
    """
    A wrapper class around a QgsGeometry which represents a
    gate through which trajectories can pass. The geometry
    must be a line.
    """

    def __init__(self, geom: QgsGeometry) -> None:
        self.__geom: QgsGeometry = geom
        self.__trajectory_count: int = 0

    def geometry(self) -> QgsGeometry:
        return self.__geom

    def trajectory_count(self) -> int:
        return self.__trajectory_count

    def count_trajectories_from_layer(self, layer: TrajectoryLayer) -> None:
        self.count_trajectories(layer.trajectories())

    def count_trajectories(self, trajectories: tuple[Trajectory, ...]) -> None:
        for trajectory in trajectories:
            if trajectory.intersects_gate(self):
                self.__trajectory_count += 1
