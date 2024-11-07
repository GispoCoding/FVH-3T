from fvh3t.core.area import Area
from fvh3t.core.trajectory import Trajectory


def test_area_trajetory_count(
    four_point_area: Area, two_node_trajectory: Trajectory, three_node_trajectory: Trajectory
):
    four_point_area.get_inside_trajectories(trajectories=(two_node_trajectory, three_node_trajectory))
    assert four_point_area.trajectory_count() == 2