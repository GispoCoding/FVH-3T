from __future__ import annotations

from typing import TYPE_CHECKING

from fvh3t.core.exceptions import InvalidDirectionException, InvalidGeometryTypeException

if TYPE_CHECKING:
    from fvh3t.core.trajectory import Trajectory
    from fvh3t.core.trajectory_layer import TrajectoryLayer

from qgis.core import QgsGeometry, QgsPointXY, QgsWkbTypes

from fvh3t.core.gate_segment import GateSegment


class Gate:
    """
    A wrapper class around a QgsGeometry which represents a
    gate through which trajectories can pass. The geometry
    must be a line.
    """

    def __init__(self, geom: QgsGeometry, *, counts_left: bool = False, counts_right: bool = False) -> None:
        if geom.type() != QgsWkbTypes.GeometryType.LineGeometry:
            msg = "Gate must be created from a line geometry!"
            raise InvalidGeometryTypeException(msg)

        self.__geom: QgsGeometry = geom
        self.__trajectory_count: int = 0

        self.__counts_left: bool = counts_left
        self.__counts_right: bool = counts_right

        if not counts_left and not counts_right:
            msg = "Gate has to count at least one direction!"
            raise InvalidDirectionException(msg)

        self.__segments: tuple[GateSegment, ...] = ()
        self.create_segments()

    def geometry(self) -> QgsGeometry:
        return self.__geom

    def trajectory_count(self) -> int:
        return self.__trajectory_count

    def counts_left(self) -> bool:
        return self.__counts_left

    def counts_right(self) -> bool:
        return self.__counts_right

    def segments(self) -> tuple[GateSegment, ...]:
        return self.__segments

    def crosses_trajectory(self, traj: Trajectory) -> bool:
        return self.__geom.crosses(traj.as_geometry())

    def create_segments(self) -> None:
        segments: list[GateSegment] = []
        polyline: list[QgsPointXY] = self.__geom.asPolyline()

        for i in range(1, len(polyline)):
            previous_point: QgsPointXY = polyline[i - 1]
            current_point: QgsPointXY = polyline[i]

            segments.append(GateSegment(previous_point, current_point))

        self.__segments = tuple(segments)

    def count_trajectories_from_layer(self, layer: TrajectoryLayer) -> None:
        self.count_trajectories(layer.trajectories())

    def count_trajectories(self, trajectories: tuple[Trajectory, ...]) -> None:
        for trajectory in trajectories:
            # check if geometries intersect at all before
            # checking which specific segments intersect
            # to save time
            if self.crosses_trajectory(trajectory):
                for traj_seg in trajectory.as_segments():
                    for segment in self.__segments:
                        # TODO: The case where a trajectory crosses
                        # the same gate multiple times is not handled
                        crosses: bool = segment.trajectory_segment_crosses(
                            traj_seg, counts_left=self.__counts_left, counts_right=self.__counts_right
                        )
                        if crosses:
                            self.__trajectory_count += 1
