from typing import TYPE_CHECKING

from qgis.core import QgsCoordinateReferenceSystem

if TYPE_CHECKING:
    from fvh3t.core.trajectory_segment import TrajectorySegment


def test_trajectory_as_segments(two_node_trajectory, three_node_trajectory):
    two_node_segments: tuple[TrajectorySegment, ...] = two_node_trajectory.as_segments()

    assert len(two_node_segments) == 1

    first_seg = two_node_segments[0]

    assert first_seg.node_a.point.x() == 0.0
    assert first_seg.node_a.point.y() == 0.0
    assert first_seg.node_b.point.x() == 0.0
    assert first_seg.node_b.point.y() == 1.0
    assert first_seg.node_a.timestamp.timestamp() == 0.1
    assert first_seg.node_b.timestamp.timestamp() == 0.2

    three_node_segments: tuple[TrajectorySegment, ...] = three_node_trajectory.as_segments()

    assert len(three_node_segments) == 2

    seg1 = three_node_segments[0]
    seg2 = three_node_segments[1]

    assert seg1.node_a.point.x() == 0.0
    assert seg1.node_a.point.y() == 0.0
    assert seg1.node_b.point.x() == 0.0
    assert seg1.node_b.point.y() == 1.0
    assert seg1.node_a.timestamp.timestamp() == 0.1
    assert seg1.node_b.timestamp.timestamp() == 0.2

    assert seg2.node_a.point.x() == 0.0
    assert seg2.node_a.point.y() == 1.0
    assert seg2.node_b.point.x() == 0.0
    assert seg2.node_b.point.y() == 2.0
    assert seg2.node_a.timestamp.timestamp() == 0.2
    assert seg2.node_b.timestamp.timestamp() == 0.3


def test_trajectory_segment_as_geometry(trajectory_segment):
    assert trajectory_segment.as_geometry().asWkt() == "LineString (0 0, 0 1)"


def test_trajectory_segment_speed(trajectory_segment):
    assert trajectory_segment.speed(QgsCoordinateReferenceSystem("EPSG:3067")) == 3.6
