from fvh3t.core.trajectory import Trajectory


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
