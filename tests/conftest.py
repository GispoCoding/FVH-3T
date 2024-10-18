"""
This class contains fixtures and common helper function to keep the test files
shorter.

pytest-qgis (https://pypi.org/project/pytest-qgis) contains the following helpful
fixtures:

* qgis_app initializes and returns fully configured QgsApplication.
  This fixture is called automatically on the start of pytest session.
* qgis_canvas initializes and returns QgsMapCanvas
* qgis_iface returns mocked QgsInterface
* new_project makes sure that all the map layers and configurations are removed.
  This should be used with tests that add stuff to QgsProject.

"""

import pytest

from fvh3t.core.trajectory import Trajectory, TrajectoryNode
from qgis.core import QgsGeometry, QgsPointXY

@pytest.fixture
def two_node_trajectory():
    return Trajectory((TrajectoryNode.from_coordinates(0, 0, 1000), TrajectoryNode.from_coordinates(0, 1, 2000)))

@pytest.fixture
def two_point_gate():
    return QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 0.5)])
