from fvh3t.core.trajectory import Trajectory, TrajectorySegment


def test_trajectory_as_geometry(two_node_trajectory: Trajectory) -> None:
    assert two_node_trajectory.as_geometry().asWkt() == "LineString (0 0, 0 1)"


def test_trajectory_average_speed(two_node_trajectory: Trajectory, three_node_trajectory: Trajectory):
    assert two_node_trajectory.average_speed() == 36.0
    assert three_node_trajectory.average_speed() == 36.0


def test_trajectory_maximum_speed(accelerating_three_node_trajectory: Trajectory):
    assert accelerating_three_node_trajectory.maximum_speed() == 96.0


def test_trajectory_length(three_node_trajectory: Trajectory):
    assert three_node_trajectory.length() == 2


def test_trajectory_duration(three_node_trajectory: Trajectory):
    assert three_node_trajectory.duration().total_seconds() == 0.2


def test_trajectory_minimum_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.minimum_size() == (0.49, 0.49, 0.49)


def test_trajectory_maximum_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.maximum_size() == (0.51, 0.51, 0.51)


def test_trajectory_average_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.average_size() == (0.50, 0.50, 0.50)


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
