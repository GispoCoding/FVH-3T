import pytest
from qgis.core import QgsPointXY

from fvh3t.core.exceptions import InvalidDirectionException
from fvh3t.core.gate_segment import GateSegment, RelativeDirection
from fvh3t.core.trajectory import TrajectoryNode, TrajectorySegment


def test_create_segments(two_point_gate, three_point_gate):
    two_point_gate.create_segments()

    segments1 = two_point_gate.segments()

    assert len(segments1) == 1

    seg1: GateSegment = segments1[0]

    assert seg1.point_a() == QgsPointXY(-0.5, 0.5)
    assert seg1.point_b() == QgsPointXY(0.5, 0.5)
    assert seg1.geometry().asWkt() == "LineString (-0.5 0.5, 0.5 0.5)"

    three_point_gate.create_segments()

    segments2 = three_point_gate.segments()

    assert len(segments2) == 2

    seg2_1 = segments2[0]
    seg2_2 = segments2[1]

    assert seg2_1.geometry().asWkt() == "LineString (1 1, 2 1)"
    assert seg2_2.geometry().asWkt() == "LineString (2 1, 2 2)"


def test_point_relative_direction():
    gate_seg1 = GateSegment(QgsPointXY(0, 0), QgsPointXY(1, 1))
    gate_seg2 = GateSegment(QgsPointXY(1, 1), QgsPointXY(0, 0))
    gate_seg3 = GateSegment(QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 1))

    point1 = QgsPointXY(0, 0.5)
    point2 = QgsPointXY(1, 0.5)
    point3 = QgsPointXY(1, 0)
    point4 = QgsPointXY(0.75, 0.75)
    point5 = QgsPointXY(0, 1)
    point6 = QgsPointXY(0.5, -0.5)
    point7 = QgsPointXY(-0.25, 0.25)
    point8 = QgsPointXY(-0.5, 1)
    point9 = QgsPointXY(1.25, 1.25)
    point10 = QgsPointXY(1, 1.25)

    assert gate_seg1.point_relative_direction(point1) == RelativeDirection.LEFT
    assert gate_seg1.point_relative_direction(point2) == RelativeDirection.RIGHT
    assert gate_seg1.point_relative_direction(point3) == RelativeDirection.RIGHT
    assert gate_seg1.point_relative_direction(point4) == RelativeDirection.COLLINEAR
    assert gate_seg1.point_relative_direction(point5) == RelativeDirection.LEFT
    assert gate_seg1.point_relative_direction(point6) == RelativeDirection.RIGHT
    assert gate_seg1.point_relative_direction(point7) == RelativeDirection.LEFT
    assert gate_seg1.point_relative_direction(point8) == RelativeDirection.LEFT
    assert gate_seg1.point_relative_direction(point9) == RelativeDirection.COLLINEAR
    assert gate_seg1.point_relative_direction(point10) == RelativeDirection.LEFT

    assert gate_seg2.point_relative_direction(point1) == RelativeDirection.RIGHT
    assert gate_seg2.point_relative_direction(point2) == RelativeDirection.LEFT
    assert gate_seg2.point_relative_direction(point3) == RelativeDirection.LEFT
    assert gate_seg2.point_relative_direction(point4) == RelativeDirection.COLLINEAR
    assert gate_seg2.point_relative_direction(point5) == RelativeDirection.RIGHT
    assert gate_seg2.point_relative_direction(point6) == RelativeDirection.LEFT
    assert gate_seg2.point_relative_direction(point7) == RelativeDirection.RIGHT
    assert gate_seg2.point_relative_direction(point8) == RelativeDirection.RIGHT
    assert gate_seg2.point_relative_direction(point9) == RelativeDirection.COLLINEAR
    assert gate_seg2.point_relative_direction(point10) == RelativeDirection.RIGHT

    assert gate_seg3.point_relative_direction(point1) == RelativeDirection.RIGHT
    assert gate_seg3.point_relative_direction(point2) == RelativeDirection.RIGHT
    assert gate_seg3.point_relative_direction(point3) == RelativeDirection.RIGHT
    assert gate_seg3.point_relative_direction(point4) == RelativeDirection.RIGHT
    assert gate_seg3.point_relative_direction(point5) == RelativeDirection.LEFT
    assert gate_seg3.point_relative_direction(point6) == RelativeDirection.RIGHT
    assert gate_seg3.point_relative_direction(point7) == RelativeDirection.RIGHT
    assert gate_seg3.point_relative_direction(point8) == RelativeDirection.LEFT
    assert gate_seg3.point_relative_direction(point9) == RelativeDirection.RIGHT
    assert gate_seg3.point_relative_direction(point10) == RelativeDirection.COLLINEAR


def test_trajectory_segment_crosses_from():
    gate_seg1 = GateSegment(QgsPointXY(0, 0), QgsPointXY(1, 1))
    gate_seg2 = GateSegment(QgsPointXY(-0.5, 1), QgsPointXY(1.5, 0))
    gate_seg3 = GateSegment(QgsPointXY(1.5, 1), QgsPointXY(-0.5, 0))

    traj_seg1 = TrajectorySegment(
        TrajectoryNode.from_coordinates(1.5, -0.5, 0, 1, 1, 1),
        TrajectoryNode.from_coordinates(-0.5, 1.5, 1000, 1, 1, 1),
    )
    traj_seg2 = TrajectorySegment(
        TrajectoryNode.from_coordinates(0.5, 1.5, 0, 1, 1, 1),
        TrajectoryNode.from_coordinates(1, -1, 1000, 1, 1, 1),
    )
    traj_seg3 = TrajectorySegment(
        TrajectoryNode.from_coordinates(-0.75, -0.5, 0, 1, 1, 1),
        TrajectoryNode.from_coordinates(1, 1.5, 1000, 1, 1, 1),
    )

    assert gate_seg1.trajectory_segment_crosses_from(traj_seg1) == RelativeDirection.RIGHT
    assert gate_seg1.trajectory_segment_crosses_from(traj_seg2) == RelativeDirection.LEFT
    with pytest.raises(InvalidDirectionException, match="Both nodes cannot be on the same side!"):
        gate_seg1.trajectory_segment_crosses_from(traj_seg3)

    assert gate_seg2.trajectory_segment_crosses_from(traj_seg1) == RelativeDirection.RIGHT
    assert gate_seg2.trajectory_segment_crosses_from(traj_seg2) == RelativeDirection.LEFT
    assert gate_seg2.trajectory_segment_crosses_from(traj_seg3) == RelativeDirection.RIGHT

    assert gate_seg3.trajectory_segment_crosses_from(traj_seg1) == RelativeDirection.LEFT
    assert gate_seg3.trajectory_segment_crosses_from(traj_seg2) == RelativeDirection.RIGHT
    assert gate_seg3.trajectory_segment_crosses_from(traj_seg3) == RelativeDirection.LEFT


def test_trajectory_segment_crosses():
    gate_seg1 = GateSegment(QgsPointXY(0, 0), QgsPointXY(1, 1))
    gate_seg2 = GateSegment(QgsPointXY(-0.5, 1), QgsPointXY(1.5, 0))
    gate_seg3 = GateSegment(QgsPointXY(1.5, 1), QgsPointXY(-0.5, 0))

    traj_seg1 = TrajectorySegment(
        TrajectoryNode.from_coordinates(1.5, -0.5, 0, 1, 1, 1),
        TrajectoryNode.from_coordinates(-0.5, 1.5, 1000, 1, 1, 1),
    )
    traj_seg2 = TrajectorySegment(
        TrajectoryNode.from_coordinates(0.5, 1.5, 0, 1, 1, 1),
        TrajectoryNode.from_coordinates(1, -1, 1000, 1, 1, 1),
    )
    traj_seg3 = TrajectorySegment(
        TrajectoryNode.from_coordinates(-0.75, -0.5, 0, 1, 1, 1),
        TrajectoryNode.from_coordinates(1, 1.5, 1000, 1, 1, 1),
    )

    assert gate_seg1.trajectory_segment_crosses(traj_seg1, counts_right=True, counts_left=False)
    assert gate_seg1.trajectory_segment_crosses(traj_seg2, counts_left=True, counts_right=True)
    assert not gate_seg1.trajectory_segment_crosses(traj_seg3, counts_right=True, counts_left=True)

    assert not gate_seg2.trajectory_segment_crosses(traj_seg1, counts_left=True, counts_right=False)
    assert gate_seg2.trajectory_segment_crosses(traj_seg2, counts_right=True, counts_left=True)
    assert not gate_seg2.trajectory_segment_crosses(traj_seg3, counts_left=True, counts_right=False)

    assert gate_seg3.trajectory_segment_crosses(traj_seg1, counts_left=True, counts_right=False)
    assert gate_seg3.trajectory_segment_crosses(traj_seg2, counts_right=True, counts_left=False)
    assert gate_seg3.trajectory_segment_crosses(traj_seg3, counts_left=True, counts_right=False)
