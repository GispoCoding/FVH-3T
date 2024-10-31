from qgis.core import QgsGeometry, QgsPointXY, QgsUnitTypes

from fvh3t.core.gate import Gate
from fvh3t.core.trajectory import Trajectory, TrajectoryNode
from fvh3t.core.trajectory_layer import TrajectoryLayer


def test_trajectory_count(qgis_point_layer_for_gate_count):
    traj_layer = TrajectoryLayer(
        qgis_point_layer_for_gate_count,
        "id",
        "timestamp",
        "width",
        "length",
        "height",
        QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
    )

    geom1 = QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 0.5)])
    gate1 = Gate(geom1, counts_positive=True)

    geom2 = QgsGeometry.fromPolylineXY([QgsPointXY(-1, 0.75), QgsPointXY(1, 1)])
    gate2 = Gate(geom2, counts_negative=True)

    geom3 = QgsGeometry.fromPolylineXY([QgsPointXY(0.5, 0), QgsPointXY(-0.75, 2)])
    gate3 = Gate(geom3, counts_negative=True, counts_positive=True)

    geom4 = QgsGeometry.fromPolylineXY([QgsPointXY(-1, -0.5), QgsPointXY(1, -0.5)])
    gate4 = Gate(geom4, counts_negative=True, counts_positive=True)

    gate1.count_trajectories_from_layer(traj_layer)
    assert gate1.trajectory_count() == 1

    gate2.count_trajectories_from_layer(traj_layer)
    assert gate2.trajectory_count() == 1

    gate3.count_trajectories_from_layer(traj_layer)
    assert gate3.trajectory_count() == 2

    gate4.count_trajectories_from_layer(traj_layer)
    assert gate4.trajectory_count() == 0


def test_geometry(two_point_gate, three_point_gate):
    assert two_point_gate.geometry().asWkt() == "LineString (-0.5 0.5, 0.5 0.5)"
    assert three_point_gate.geometry().asWkt() == "LineString (1 1, 2 1, 2 2)"


def test_crosses_trajectory(two_point_gate, three_point_gate, two_node_trajectory):
    assert two_point_gate.crosses_trajectory(two_node_trajectory)
    assert not three_point_gate.crosses_trajectory(two_node_trajectory)


def test_trajectory_crosses_topological(two_point_gate):
    traj1 = Trajectory(
        (
            TrajectoryNode.from_coordinates(0, 0, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 0.5, 500, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 1, 1000, 0, 0, 0),
        ),
    )

    traj2 = Trajectory(
        (
            TrajectoryNode.from_coordinates(0, 1, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 0.5, 500, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 0, 1000, 0, 0, 0),
        ),
    )

    traj3 = Trajectory(
        (
            TrajectoryNode.from_coordinates(0, -1, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, -0.5, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 0, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 0.5, 500, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 1, 1000, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 2, 1000, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 3, 1000, 0, 0, 0),
        ),
    )

    traj4 = Trajectory(
        (
            TrajectoryNode.from_coordinates(0, 3, 1000, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 2, 1000, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 1, 1000, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 0.5, 500, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 0, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, -0.5, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, -1, 0, 0, 0, 0),
        ),
    )

    two_point_gate.set_counts_negative(state=False)

    two_point_gate.count_trajectories([traj1, traj2, traj3, traj4])

    assert two_point_gate.trajectory_count() == 2


def test_calculate_two_point_gate_average_speed(two_point_gate):
    two_point_gate.set_counts_negative(state=False)

    traj1 = Trajectory(
        (
            TrajectoryNode.from_coordinates(0, 0, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(0, 1, 100, 0, 0, 0),
        )
    )

    traj2 = Trajectory(
        (TrajectoryNode.from_coordinates(0, 0, 0, 0, 0, 0), TrajectoryNode.from_coordinates(0, 1, 200, 0, 0, 0))
    )

    two_point_gate.count_trajectories([traj1, traj2])

    assert two_point_gate.trajectory_count() == 2
    assert two_point_gate.average_speed() == 27.0


def test_calculate_three_point_gate_average_speed(three_point_gate):
    three_point_gate.set_counts_negative(state=False)

    traj1 = Trajectory(
        (
            TrajectoryNode.from_coordinates(1.5, 0, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(1.5, 2, 100, 0, 0, 0),
        )
    )

    traj2 = Trajectory(
        (
            TrajectoryNode.from_coordinates(3, 1.5, 0, 0, 0, 0),
            TrajectoryNode.from_coordinates(1, 1.5, 200, 0, 0, 0),
        )
    )

    three_point_gate.count_trajectories([traj1, traj2])

    assert three_point_gate.trajectory_count() == 2
    assert three_point_gate.average_speed() == 54.0
