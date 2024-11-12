from __future__ import annotations

from typing import TYPE_CHECKING

from fvh3t.core.exceptions import InvalidDirectionException, InvalidGeometryTypeException

if TYPE_CHECKING:
    from fvh3t.core.trajectory import Trajectory, TrajectorySegment
    from fvh3t.core.trajectory_layer import TrajectoryLayer

from qgis.core import QgsCoordinateReferenceSystem, QgsGeometry, QgsPointXY, QgsWkbTypes

from fvh3t.core.gate_segment import GateSegment, RelativeDirection


class Gate:
    """
    A wrapper class around a QgsGeometry which represents a
    gate through which trajectories can pass. The geometry
    must be a line.
    """

    def __init__(
        self,
        geom: QgsGeometry,
        name: str,
        *,
        counts_negative: bool = False,
        counts_positive: bool = False,
    ) -> None:
        if geom.type() != QgsWkbTypes.GeometryType.LineGeometry:
            msg = "Gate must be created from a line geometry!"
            raise InvalidGeometryTypeException(msg)

        self.__geom: QgsGeometry = geom
        self.__trajectory_count: int = 0
        self.__trajectory_count_negative: int = 0
        self.__trajectory_count_positive: int = 0

        self.__name: str = name

        self.__counts_negative: bool = counts_negative
        self.__counts_positive: bool = counts_positive

        self.__average_speed: float = 0.0
        self.__average_acceleration: float = 0.0

        if not counts_negative and not counts_positive:
            msg = "Gate has to count at least one direction!"
            raise InvalidDirectionException(msg)

        self.__segments: tuple[GateSegment, ...] = ()
        self.create_segments()

    def name(self) -> str:
        return self.__name

    def set_counts_negative(self, *, state: bool) -> None:
        self.__counts_negative = state

    def set_counts_positive(self, *, state: bool) -> None:
        self.__counts_positive = state

    def geometry(self) -> QgsGeometry:
        return self.__geom

    def trajectory_count(self) -> int:
        return self.__trajectory_count

    def trajectory_count_negative(self) -> int:
        return self.__trajectory_count_negative

    def trajectory_count_positive(self) -> int:
        return self.__trajectory_count_positive

    def average_speed(self) -> float:
        return self.__average_speed

    def average_acceleration(self) -> float:
        return self.__average_acceleration

    def counts_negative(self) -> bool:
        return self.__counts_negative

    def counts_positive(self) -> bool:
        return self.__counts_positive

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

    def count_trajectories(
        self, trajectories: tuple[Trajectory, ...], trajectory_layer: TrajectoryLayer | None = None
    ) -> None:
        speed = 0.0
        acceleration = 0.0
        crs = trajectory_layer.crs() if trajectory_layer else QgsCoordinateReferenceSystem("EPSG:3067")
        for trajectory in trajectories:
            # check if geometries cross at all before
            # checking which specific segments cross
            # to save time
            if self.crosses_trajectory(trajectory):
                traj_segments: tuple[TrajectorySegment, ...] = trajectory.as_segments()
                for i in range(len(traj_segments)):
                    traj_seg: TrajectorySegment = traj_segments[i]
                    for gate_segment in self.__segments:
                        # TODO: The case where a trajectory crosses
                        # the same gate multiple times is not handled

                        previous_traj_seg: TrajectorySegment | None = traj_segments[i - 1] if i > 0 else None
                        crosses: bool | RelativeDirection = gate_segment.trajectory_segment_crosses(
                            traj_seg,
                            previous_traj_seg,
                            counts_negative=self.__counts_negative,
                            counts_positive=self.__counts_positive,
                        )
                        if isinstance(crosses, RelativeDirection):
                            if crosses == RelativeDirection.LEFT:
                                self.__trajectory_count_negative += 1
                            elif crosses == RelativeDirection.RIGHT:
                                self.__trajectory_count_positive += 1
                        if crosses is not False:
                            self.__trajectory_count += 1
                            current_speed = traj_seg.speed(crs)
                            speed += current_speed

                            if previous_traj_seg is not None:
                                previous_speed = previous_traj_seg.speed(crs)

                                # km/h -> m/s
                                current_speed /= 3.6
                                previous_speed /= 3.6

                                acceleration += (current_speed - previous_speed) / (
                                    traj_seg.node_b.timestamp - previous_traj_seg.node_a.timestamp
                                ).total_seconds()

        if self.trajectory_count() > 0:
            self.__average_speed = speed / self.trajectory_count()
            self.__average_acceleration = acceleration / self.trajectory_count()
