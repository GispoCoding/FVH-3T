from fvh3t.core.trajectory import Trajectory
from qgis.core import QgsGeometry, QgsPointXY

def test_trajectory_as_geometry(two_node_trajectory: Trajectory) -> None:
    assert two_node_trajectory.as_geometry().asWkt() == "LineString (0 0, 0 1)"

def test_trajectory_intersects(two_node_trajectory):
    geom1 = QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 0.5)])
    geom2 = QgsGeometry.fromPolylineXY([QgsPointXY(-1, -1), QgsPointXY(-2, -2)])

    assert two_node_trajectory.intersects(geom1)
    assert not two_node_trajectory.intersects(geom2)

