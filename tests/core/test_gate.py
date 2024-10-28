from qgis.core import QgsGeometry, QgsPointXY, QgsUnitTypes

from fvh3t.core.gate import Gate
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
    gate1 = Gate(geom1, counts_right=True)

    geom2 = QgsGeometry.fromPolylineXY([QgsPointXY(-1, 0.75), QgsPointXY(1, 1)])
    gate2 = Gate(geom2, counts_left=True)

    geom3 = QgsGeometry.fromPolylineXY([QgsPointXY(0.5, 0), QgsPointXY(-0.75, 2)])
    gate3 = Gate(geom3, counts_left=True, counts_right=True)

    geom4 = QgsGeometry.fromPolylineXY([QgsPointXY(-1, -0.5), QgsPointXY(1, -0.5)])
    gate4 = Gate(geom4, counts_left=True, counts_right=True)

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
