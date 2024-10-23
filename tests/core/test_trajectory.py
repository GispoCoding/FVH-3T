from qgis.core import QgsGeometry, QgsPointXY, QgsUnitTypes

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
    traj_layer = TrajectoryLayer(
        qgis_point_layer, "id", "timestamp", "width", "length", "height", QgsUnitTypes.TemporalUnit.TemporalMilliseconds
    )
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

    assert nodes1[0].timestamp == 100
    assert nodes1[1].timestamp == 200
    assert nodes1[2].timestamp == 300

    assert nodes2[0].timestamp == 500
    assert nodes2[1].timestamp == 600
    assert nodes2[2].timestamp == 700


def test_trajectory_layer_create_line_layer(qgis_point_layer):
    traj_layer = TrajectoryLayer(
        qgis_point_layer, "id", "timestamp", "width", "length", "height", QgsUnitTypes.TemporalUnit.TemporalMilliseconds
    )
    traj_layer.create_trajectories()

    line_layer = traj_layer.as_line_layer()

    assert line_layer is not None
    assert line_layer.featureCount() == 2

    feat1 = line_layer.getFeature(1)
    feat2 = line_layer.getFeature(2)

    assert feat1.geometry().asWkt() == "LineString (0 0, 1 0, 2 0)"
    assert feat2.geometry().asWkt() == "LineString (5 1, 5 2, 5 3)"

    assert feat1.attribute("average_speed") == 36.0
    assert feat2.attribute("average_speed") == 36.0


def test_trajectory_layer_node_ordering(qgis_point_layer_non_ordered):
    traj_layer = TrajectoryLayer(
        qgis_point_layer_non_ordered,
        "id",
        "timestamp",
        "width",
        "length",
        "height",
        QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
    )
    traj_layer.create_trajectories()

    trajectories = traj_layer.trajectories()

    assert len(trajectories) == 1

    nodes = trajectories[0].nodes()

    assert len(nodes) == 3

    assert nodes[0].timestamp == 1000
    assert nodes[1].timestamp == 3000
    assert nodes[2].timestamp == 6000


def test_trajectory_average_speed(two_node_trajectory: Trajectory, three_node_trajectory: Trajectory):
    assert two_node_trajectory.average_speed() == 36.0
    assert three_node_trajectory.average_speed() == 36.0


def test_trajectory_maximum_speed(accelerating_three_node_trajectory: Trajectory):
    assert accelerating_three_node_trajectory.maximum_speed() == 96.0


def test_trajectory_length(three_node_trajectory: Trajectory):
    assert three_node_trajectory.length() == 2


def test_trajectory_duration(three_node_trajectory: Trajectory):
    assert three_node_trajectory.duration() == 200


def test_trajectory_minimum_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.minimum_size() == (0.49, 0.49, 0.49)


def test_trajectory_maximum_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.maximum_size() == (0.51, 0.51, 0.51)


def test_trajectory_average_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.average_size() == (0.50, 0.50, 0.50)
