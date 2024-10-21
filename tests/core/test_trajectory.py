from qgis.core import QgsGeometry, QgsPointXY

from fvh3t.core.gate import Gate
from fvh3t.core.trajectory import Trajectory, TrajectoryLayer, TrajectoryNode


def test_trajectory_as_geometry(two_node_trajectory: Trajectory) -> None:
    assert two_node_trajectory.as_geometry().asWkt() == "LineString (0 0, 0 1)"


def test_trajectory_intersects_gate(two_node_trajectory):
    geom1 = QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 0.5)])
    geom2 = QgsGeometry.fromPolylineXY([QgsPointXY(-1, -1), QgsPointXY(-2, -2)])

    gate1 = Gate(geom1)
    gate2 = Gate(geom2)

    assert two_node_trajectory.intersects_gate(gate1)
    assert not two_node_trajectory.intersects_gate(gate2)


def test_trajectory_layer_create_trajectories(qgis_point_layer):
    traj_layer = TrajectoryLayer(qgis_point_layer, "id", "timestamp")
    traj_layer.create_trajectories()

    trajectories: tuple[Trajectory, ...] = traj_layer.trajectories()
    assert len(trajectories) == 2

    traj1: Trajectory = trajectories[0]
    traj2: Trajectory = trajectories[1]

    assert traj1.as_geometry().asWkt() == "LineString (0 0, 1 0, 2 0)"
    assert traj2.as_geometry().asWkt() == "LineString (5 1, 5 2, 5 3)"

    nodes1: tuple[TrajectoryNode, ...] = traj1.nodes()
    nodes2: tuple[TrajectoryNode, ...] = traj2.nodes()

    assert len(nodes1) == 3
    assert len(nodes2) == 3

    assert nodes1[0].timestamp == 1000
    assert nodes1[1].timestamp == 2000
    assert nodes1[2].timestamp == 3000

    assert nodes2[0].timestamp == 5000
    assert nodes2[1].timestamp == 6000
    assert nodes2[2].timestamp == 7000


def test_trajectory_layer_create_line_layer(qgis_point_layer):
    traj_layer = TrajectoryLayer(qgis_point_layer, "id", "timestamp")
    traj_layer.create_trajectories()

    line_layer = traj_layer.as_line_layer()

    assert line_layer is not None
    assert line_layer.featureCount() == 2

    feat1 = line_layer.getFeature(1)
    feat2 = line_layer.getFeature(2)

    assert feat1.geometry().asWkt() == "LineString (0 0, 1 0, 2 0)"
    assert feat2.geometry().asWkt() == "LineString (5 1, 5 2, 5 3)"

    # FIXME: change when average_speed is implemented
    assert feat1.attribute("average_speed") == 0.0
    assert feat2.attribute("average_speed") == 0.0
