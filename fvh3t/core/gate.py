from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from fvh3t.core.exceptions import InvalidDirectionException, InvalidGeometryTypeException, InvalidLayerException

if TYPE_CHECKING:
    from fvh3t.core.trajectory import Trajectory, TrajectoryLayer, TrajectorySegment

from qgis.core import QgsFeatureSource, QgsGeometry, QgsPointXY, QgsVectorLayer, QgsWkbTypes


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

    def trajectory_segment_passes(self, traj_seg: TrajectorySegment, *, counts_left: bool, counts_right: bool) -> bool:
        intersects = self.__geom.intersects(traj_seg.as_geometry())

        if not intersects:
            return False

        if counts_left and counts_right:
            return True

        passes_from: RelativeDirection = self._trajectory_segment_passes_from(traj_seg)

        if counts_left and passes_from == RelativeDirection.LEFT:
            return True

        return counts_right and passes_from == RelativeDirection.RIGHT

    def _trajectory_segment_passes_from(self, segment: TrajectorySegment) -> RelativeDirection:
        node_a_dir: RelativeDirection = self.point_relative_direction(segment.node_a.point)
        node_b_dir: RelativeDirection = self.point_relative_direction(segment.node_b.point)

        passes_from: RelativeDirection = RelativeDirection.UNKNOWN

        # node A should always be the first node, timewise

        if node_a_dir == RelativeDirection.LEFT and node_b_dir == RelativeDirection.RIGHT:
            passes_from = RelativeDirection.LEFT
        elif node_a_dir == RelativeDirection.RIGHT and node_b_dir == RelativeDirection.LEFT:
            passes_from = RelativeDirection.RIGHT
        elif node_a_dir == RelativeDirection.COLLINEAR and node_b_dir == RelativeDirection.RIGHT:
            passes_from = RelativeDirection.LEFT
        elif (
            node_a_dir == RelativeDirection.COLLINEAR
            and node_b_dir == RelativeDirection.LEFT
            or node_a_dir == RelativeDirection.RIGHT
            and node_b_dir == RelativeDirection.COLLINEAR
        ):
            passes_from = RelativeDirection.RIGHT
        elif node_a_dir == RelativeDirection.LEFT and node_b_dir == RelativeDirection.COLLINEAR:
            passes_from = RelativeDirection.LEFT
        elif node_a_dir == RelativeDirection.COLLINEAR and node_b_dir == RelativeDirection.COLLINEAR:
            # i.e. the trajectory segment is exactly
            # on this gate segment.
            # realistically this should be extremely rare,
            # but regardless we have to deal with this
            # edge case.
            passes_from = RelativeDirection.COLLINEAR
        elif node_a_dir == node_b_dir:
            # it is assumed that it has already been checked
            # that the trajectory segment intersects
            # this gate segment.
            # therefore this should never happen and
            # we throw an error

            msg = "Both nodes cannot be on the same side!"
            raise InvalidDirectionException(msg)
        else:
            # this would require either dir
            # being UNKNOWN which should never
            # happen, so throw an error

            msg = "Directions cannot be unkown!"
            raise InvalidDirectionException(msg)

        return passes_from

    def point_relative_direction(self, point: QgsPointXY) -> RelativeDirection:
        pos: float = (
            self.__point_b.x()
            - self.__point_a.x() * (point.y() - self.__point_a.y())
            - (self.__point_b.y() - self.__point_a.y()) * (point.x() - self.__point_a.x())
        )
        if pos > 0:
            direction = RelativeDirection.LEFT
        elif pos < 0:
            direction = RelativeDirection.RIGHT
        else:
            direction = RelativeDirection.COLLINEAR

        return direction


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
            if self.__geom.intersects(trajectory.as_geometry()):
                for traj_seg in trajectory.as_segments():
                    for segment in self.__segments:
                        # TODO: The case where a trajectory passes
                        # the same gate multiple times is not handled
                        passes: bool = segment.trajectory_segment_passes(
                            traj_seg, counts_left=self.__counts_left, counts_right=self.__counts_right
                        )
                        if passes:
                            self.__trajectory_count += 1


class GateLayer:
    """
    Wrapper around a QgsVectorLayer object from which gates
    can be instantiated, i.e.

    1. is a line layer
    2. has a valid "counts left" field
    2. has a valid "counts right" field
    """

    def __init__(
        self,
        layer: QgsVectorLayer,
        counts_left_field: str,
        counts_right_field: str,
    ) -> None:
        self.__layer: QgsVectorLayer = layer
        self.__counts_left_field = counts_left_field
        self.__counts_right_field = counts_right_field

        if not self.is_valid():
            msg = "GateLayer could not be properly created!"
            raise InvalidLayerException(msg)

        self.__gates: tuple[Gate, ...] = ()
        self.create_gates()

    def create_gates(self) -> None:
        counts_left_field_idx: int = self.__layer.fields().indexOf(self.__counts_left_field)
        counts_right_field_idx: int = self.__layer.fields().indexOf(self.__counts_right_field)

        # TODO: Check that these are bool fields

        gates: list[Gate] = []

        for feature in self.__layer.getFeatures():
            counts_left: bool = feature[counts_left_field_idx]
            counts_right: bool = feature[counts_right_field_idx]

            gate = Gate(feature.geometry(), counts_left=counts_left, counts_right=counts_right)

            gates.append(gate)

        self.__gates = tuple(gates)

    def gates(self) -> tuple[Gate, ...]:
        return self.__gates

    def is_valid(self) -> bool:
        is_layer_valid: bool = self.__layer.isValid()
        if not is_layer_valid:
            msg = "Layer is not valid."
            raise ValueError(msg)

        is_point_layer: bool = self.__layer.geometryType() == QgsWkbTypes.GeometryType.PointGeometry
        if not is_point_layer:
            msg = "Layer is not a point layer."
            raise ValueError(msg)

        has_features: bool = self.__layer.hasFeatures() == QgsFeatureSource.FeatureAvailability.FeaturesAvailable
        if not has_features:
            msg = "Layer has no features."
            raise ValueError(msg)

        counts_left_field_exists: bool = self.__layer.fields().indexFromName(self.__counts_left_field) != -1
        if not counts_left_field_exists:
            msg = "Counts left field not found in the layer."
            raise ValueError(msg)

        counts_right_field_exists: bool = self.__layer.fields().indexFromName(self.__counts_right_field) != -1
        if not counts_right_field_exists:
            msg = "Counts right field not found in the layer."
            raise ValueError(msg)

        return True
