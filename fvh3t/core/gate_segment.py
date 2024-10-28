from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from qgis.core import QgsGeometry, QgsPointXY

from fvh3t.core.exceptions import InvalidDirectionException

if TYPE_CHECKING:
    from fvh3t.core.trajectory_segment import TrajectorySegment


class RelativeDirection(Enum):
    LEFT = 1
    RIGHT = 2
    COLLINEAR = 3
    UNKNOWN = 4


class GateSegment:
    """
    Class representing one segment of a Gate.
    """

    def __init__(self, point_a: QgsPointXY, point_b: QgsPointXY) -> None:
        self.__point_a: QgsPointXY = point_a
        self.__point_b: QgsPointXY = point_b

        self.__geom = QgsGeometry.fromPolylineXY([point_a, point_b])

    def point_a(self) -> QgsPointXY:
        return self.__point_a

    def point_b(self) -> QgsPointXY:
        return self.__point_b

    def geometry(self) -> QgsGeometry:
        return self.__geom

    def trajectory_segment_crosses(self, traj_seg: TrajectorySegment, *, counts_left: bool, counts_right: bool) -> bool:
        crosses = self.__geom.crosses(traj_seg.as_geometry())

        if not crosses:
            if self.__geom.intersects(traj_seg.as_geometry()):
                # TODO: Handle case where the segment doesn't cross this segment
                # but instead intersects it. In practice this means that when a trajectory
                # has a vertex exactly on this segment we cannot rely on calculating
                # the crossing direction from the singular segment.
                # Realistically the chances of a trajectory node landing exactly on the
                # gate segment should be extremely rare, but regardless we do need
                # to deal with that... BUT right now in the interest of moving things
                # forwards I'm leaving this as a TODO
                msg = "Cannot determine direction from trajectory segment!"
                raise InvalidDirectionException(msg)

            return False

        if counts_left and counts_right:
            return True

        crosses_from: RelativeDirection = self.trajectory_segment_crosses_from(traj_seg)

        if counts_left and crosses_from == RelativeDirection.LEFT:
            return True

        return counts_right and crosses_from == RelativeDirection.RIGHT

    def trajectory_segment_crosses_from(self, segment: TrajectorySegment) -> RelativeDirection:
        """
        Check which relative direction a trajectory
        segment crosses this gate segment from. There are
        two assumptions:

        1) the segments actually cross (should be checked beforehand)
           an error is raised if this is not the case
        2) node A of the trajectory segment is first, timewise
        """
        node_a_dir: RelativeDirection = self.point_relative_direction(segment.node_a.point)
        node_b_dir: RelativeDirection = self.point_relative_direction(segment.node_b.point)

        crosses_from: RelativeDirection = RelativeDirection.UNKNOWN

        if node_a_dir == RelativeDirection.LEFT and node_b_dir == RelativeDirection.RIGHT:
            crosses_from = RelativeDirection.LEFT
        elif node_a_dir == RelativeDirection.RIGHT and node_b_dir == RelativeDirection.LEFT:
            crosses_from = RelativeDirection.RIGHT
        else:
            # NOTE: this means that the segments do *not* cross i.e.
            #   1. one or both nodes are collinear with this gate segment
            #   2. both nodes are on the same side
            # This should never happen so raise an error.

            msg = "Segments do not cross!"
            raise InvalidDirectionException(msg)

            # NOTE: Technically this else block would catch
            # cases where either node_dir is UNKNOWN, but
            # since point_relative_direction() can't return
            # UNKNOWN we should be able to assume that
            # the cause to always be that the segments
            # don't actually cross

        return crosses_from

    def point_relative_direction(self, point: QgsPointXY) -> RelativeDirection:
        pos: float = (point.x() - self.__point_a.x()) * (self.__point_b.y() - self.__point_a.y()) - (
            point.y() - self.__point_a.y()
        ) * (self.__point_b.x() - self.__point_a.x())

        if pos > 0:
            direction = RelativeDirection.RIGHT
        elif pos < 0:
            direction = RelativeDirection.LEFT
        else:
            direction = RelativeDirection.COLLINEAR

        return direction
