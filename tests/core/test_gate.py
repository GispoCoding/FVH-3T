from qgis.core import QgsGeometry, QgsPointXY, QgsUnitTypes

from fvh3t.core.gate import Gate
from fvh3t.core.trajectory import TrajectoryLayer


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
    traj_layer.create_trajectories()

    geom1 = QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 0.5)])
    gate1 = Gate(geom1)

    geom2 = QgsGeometry.fromPolylineXY([QgsPointXY(0.10, 0.5), QgsPointXY(0.5, 0.5)])
    gate2 = Gate(geom2)

    geom3 = QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, -0.5), QgsPointXY(0.5, -0.5)])
    gate3 = Gate(geom3)

    gate1.count_trajectories_from_layer(traj_layer)
    assert gate1.trajectory_count() == 2

    gate2.count_trajectories_from_layer(traj_layer)
    assert gate2.trajectory_count() == 1

    gate3.count_trajectories_from_layer(traj_layer)
    assert gate3.trajectory_count() == 0
