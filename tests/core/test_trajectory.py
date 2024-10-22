from qgis.core import QgsGeometry, QgsPointXY

from fvh3t.core.gate import Gate
from fvh3t.core.trajectory import Trajectory


def test_trajectory_as_geometry(two_node_trajectory: Trajectory) -> None:
    assert two_node_trajectory.as_geometry().asWkt() == "LineString (0 0, 0 1)"


def test_trajectory_intersects_gate(two_node_trajectory):
    geom1 = QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 0.5)])
    geom2 = QgsGeometry.fromPolylineXY([QgsPointXY(-1, -1), QgsPointXY(-2, -2)])

    gate1 = Gate(geom1)
    gate2 = Gate(geom2)

    assert two_node_trajectory.intersects_gate(gate1)
    assert not two_node_trajectory.intersects_gate(gate2)


def test_trajectory_average_speed(two_node_trajectory: Trajectory, three_node_trajectory: Trajectory):
    assert two_node_trajectory.average_speed() == 0.001
    assert three_node_trajectory.average_speed() == 0.001
