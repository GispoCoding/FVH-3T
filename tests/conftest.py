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
from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant

from fvh3t.core.gate import Gate
from fvh3t.core.trajectory import Trajectory, TrajectoryNode


@pytest.fixture
def two_node_trajectory():
    return Trajectory((TrajectoryNode.from_coordinates(0, 0, 1000), TrajectoryNode.from_coordinates(0, 1, 2000)))


@pytest.fixture
def three_node_trajectory():
    return Trajectory(
        (
            TrajectoryNode.from_coordinates(0, 0, 1000),
            TrajectoryNode.from_coordinates(0, 1, 2000),
            TrajectoryNode.from_coordinates(0, 2, 3000),
        )
    )


@pytest.fixture
def two_point_gate():
    return Gate(QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 0.5)]))


@pytest.fixture
def qgis_point_layer():
    layer = QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("id", QVariant.Int))
    layer.addAttribute(QgsField("timestamp", QVariant.Int))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([1, 1000])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))

    traj1_f2 = QgsFeature(layer.fields())
    traj1_f2.setAttributes([1, 2000])
    traj1_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 0)))

    traj1_f3 = QgsFeature(layer.fields())
    traj1_f3.setAttributes([1, 3000])
    traj1_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(2, 0)))

    traj2_f1 = QgsFeature(layer.fields())
    traj2_f1.setAttributes([2, 5000])
    traj2_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(5, 1)))

    traj2_f2 = QgsFeature(layer.fields())
    traj2_f2.setAttributes([2, 6000])
    traj2_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(5, 2)))

    traj2_f3 = QgsFeature(layer.fields())
    traj2_f3.setAttributes([2, 7000])
    traj2_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(5, 3)))

    layer.addFeature(traj1_f1)
    layer.addFeature(traj1_f2)
    layer.addFeature(traj1_f3)

    layer.addFeature(traj2_f1)
    layer.addFeature(traj2_f2)
    layer.addFeature(traj2_f3)

    layer.commitChanges()

    return layer
