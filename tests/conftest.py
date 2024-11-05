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
from fvh3t.core.trajectory import Trajectory, TrajectoryNode, TrajectorySegment


@pytest.fixture
def two_node_trajectory():
    return Trajectory(
        (TrajectoryNode.from_coordinates(0, 0, 100, 1, 1, 1), TrajectoryNode.from_coordinates(0, 1, 200, 1, 1, 1))
    )


@pytest.fixture
def three_node_trajectory():
    return Trajectory(
        (
            TrajectoryNode.from_coordinates(0, 0, 100, 1, 1, 1),
            TrajectoryNode.from_coordinates(0, 1, 200, 1, 1, 1),
            TrajectoryNode.from_coordinates(0, 2, 300, 1, 1, 1),
        )
    )


@pytest.fixture
def accelerating_three_node_trajectory():
    return Trajectory(
        (
            TrajectoryNode.from_coordinates(0, 0, 100, 1, 1, 1),
            TrajectoryNode.from_coordinates(0, 1, 150, 1, 1, 1),
            TrajectoryNode.from_coordinates(0, 5, 300, 1, 1, 1),
        )
    )


@pytest.fixture
def size_changing_trajectory():
    return Trajectory(
        (
            TrajectoryNode.from_coordinates(0, 0, 100, 0.5, 0.5, 0.5),
            TrajectoryNode.from_coordinates(0, 1, 200, 0.51, 0.51, 0.51),
            TrajectoryNode.from_coordinates(0, 2, 300, 0.49, 0.49, 0.49),
        )
    )


@pytest.fixture
def two_point_gate():
    return Gate(
        QgsGeometry.fromPolylineXY([QgsPointXY(-0.5, 0.5), QgsPointXY(0.5, 0.5)]),
        name="two_point_gate",
        counts_negative=True,
        counts_positive=True,
    )


@pytest.fixture
def three_point_gate():
    return Gate(
        QgsGeometry.fromPolylineXY([QgsPointXY(1, 1), QgsPointXY(2, 1), QgsPointXY(2, 2)]),
        name="three_point_gate",
        counts_negative=True,
        counts_positive=True,
    )


@pytest.fixture
def trajectory_segment():
    return TrajectorySegment(
        TrajectoryNode.from_coordinates(0, 0, 0, 1, 1, 1),
        TrajectoryNode.from_coordinates(0, 1, 1000, 1, 1, 1),
    )


@pytest.fixture
def qgis_single_point_layer():
    layer = QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("id", QVariant.Int))
    layer.addAttribute(QgsField("timestamp", QVariant.Double))
    layer.addAttribute(QgsField("width", QVariant.Int))
    layer.addAttribute(QgsField("length", QVariant.Int))
    layer.addAttribute(QgsField("height", QVariant.Int))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([1, 100, 1, 1, 1])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))

    layer.addFeature(traj1_f1)

    layer.commitChanges()

    return layer


@pytest.fixture
def qgis_point_layer():
    layer = QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("id", QVariant.Int))
    layer.addAttribute(QgsField("timestamp", QVariant.Double))
    layer.addAttribute(QgsField("width", QVariant.Int))
    layer.addAttribute(QgsField("length", QVariant.Int))
    layer.addAttribute(QgsField("height", QVariant.Int))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([1, 100, 1, 1, 1])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))

    traj1_f2 = QgsFeature(layer.fields())
    traj1_f2.setAttributes([1, 200, 1, 1, 1])
    traj1_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 0)))

    traj1_f3 = QgsFeature(layer.fields())
    traj1_f3.setAttributes([1, 300, 1, 1, 1])
    traj1_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(2, 0)))

    traj2_f1 = QgsFeature(layer.fields())
    traj2_f1.setAttributes([2, 500, 1, 1, 1])
    traj2_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(5, 1)))

    traj2_f2 = QgsFeature(layer.fields())
    traj2_f2.setAttributes([2, 600, 1, 1, 1])
    traj2_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(5, 2)))

    traj2_f3 = QgsFeature(layer.fields())
    traj2_f3.setAttributes([2, 700, 1, 1, 1])
    traj2_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(5, 3)))

    layer.addFeature(traj1_f1)
    layer.addFeature(traj1_f2)
    layer.addFeature(traj1_f3)

    layer.addFeature(traj2_f1)
    layer.addFeature(traj2_f2)
    layer.addFeature(traj2_f3)

    layer.commitChanges()

    return layer


@pytest.fixture
def qgis_point_layer_non_ordered():
    layer = QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("id", QVariant.Int))
    layer.addAttribute(QgsField("timestamp", QVariant.Int))
    layer.addAttribute(QgsField("width", QVariant.Int))
    layer.addAttribute(QgsField("length", QVariant.Int))
    layer.addAttribute(QgsField("height", QVariant.Int))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([1, 3000, 1, 1, 1])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))

    traj1_f2 = QgsFeature(layer.fields())
    traj1_f2.setAttributes([1, 6000, 1, 1, 1])
    traj1_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 0)))

    traj1_f3 = QgsFeature(layer.fields())
    traj1_f3.setAttributes([1, 1000, 1, 1, 1])
    traj1_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(2, 0)))

    layer.addFeature(traj1_f1)
    layer.addFeature(traj1_f2)
    layer.addFeature(traj1_f3)

    layer.commitChanges()

    return layer


@pytest.fixture
def qgis_vector_layer():
    return QgsVectorLayer()


@pytest.fixture
def qgis_line_layer():
    return QgsVectorLayer("LineString?crs=EPSG:3067", "Line Layer", "memory")


@pytest.fixture
def qgis_point_layer_no_features():
    return QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")


@pytest.fixture
def qgis_point_layer_no_additional_fields():
    layer = QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("timestamp", QVariant.Int))
    layer.addAttribute(QgsField("width", QVariant.Int))
    layer.addAttribute(QgsField("length", QVariant.Int))
    layer.addAttribute(QgsField("height", QVariant.Int))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([3000, 1, 1, 1])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))

    traj1_f2 = QgsFeature(layer.fields())
    traj1_f2.setAttributes([6000, 1, 1, 1])
    traj1_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 0)))

    traj1_f3 = QgsFeature(layer.fields())
    traj1_f3.setAttributes([1000, 1, 1, 1])
    traj1_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(2, 0)))

    layer.addFeature(traj1_f1)
    layer.addFeature(traj1_f2)
    layer.addFeature(traj1_f3)

    layer.commitChanges()

    return layer


@pytest.fixture
def qgis_point_layer_wrong_type():
    layer = QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("id", QVariant.Int))
    layer.addAttribute(QgsField("timestamp", QVariant.String))
    layer.addAttribute(QgsField("width", QVariant.Int))
    layer.addAttribute(QgsField("length", QVariant.Int))
    layer.addAttribute(QgsField("height", QVariant.Int))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([1, 3000, 1, 1, 1])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))

    traj1_f2 = QgsFeature(layer.fields())
    traj1_f2.setAttributes([1, 6000, 1, 1, 1])
    traj1_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 0)))

    traj1_f3 = QgsFeature(layer.fields())
    traj1_f3.setAttributes([1, 1000, 1, 1, 1])
    traj1_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(2, 0)))

    layer.addFeature(traj1_f1)
    layer.addFeature(traj1_f2)
    layer.addFeature(traj1_f3)

    layer.commitChanges()

    return layer


@pytest.fixture
def qgis_point_layer_for_gate_count():
    layer = QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("id", QVariant.Int))
    layer.addAttribute(QgsField("timestamp", QVariant.Double))
    layer.addAttribute(QgsField("width", QVariant.Int))
    layer.addAttribute(QgsField("length", QVariant.Int))
    layer.addAttribute(QgsField("height", QVariant.Int))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([1, 100, 1, 1, 1])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))

    traj1_f2 = QgsFeature(layer.fields())
    traj1_f2.setAttributes([1, 200, 1, 1, 1])
    traj1_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 1)))

    traj1_f3 = QgsFeature(layer.fields())
    traj1_f3.setAttributes([1, 300, 1, 1, 1])
    traj1_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 2)))

    traj2_f1 = QgsFeature(layer.fields())
    traj2_f1.setAttributes([2, 500, 1, 1, 1])
    traj2_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.25, 2)))

    traj2_f2 = QgsFeature(layer.fields())
    traj2_f2.setAttributes([2, 600, 1, 1, 1])
    traj2_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.25, 1)))

    traj2_f3 = QgsFeature(layer.fields())
    traj2_f3.setAttributes([2, 700, 1, 1, 1])
    traj2_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.25, 0)))

    layer.addFeature(traj1_f1)
    layer.addFeature(traj1_f2)
    layer.addFeature(traj1_f3)

    layer.addFeature(traj2_f1)
    layer.addFeature(traj2_f2)
    layer.addFeature(traj2_f3)

    layer.commitChanges()

    return layer


@pytest.fixture
def qgis_gate_line_layer():
    layer = QgsVectorLayer("LineString?crs=EPSG:3067", "Line Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("name", QVariant.String))
    layer.addAttribute(QgsField("counts_negative", QVariant.Bool))
    layer.addAttribute(QgsField("counts_positive", QVariant.Bool))

    gate1 = QgsFeature(layer.fields())
    gate1.setAttributes(["name", True, True])
    gate1.setGeometry(
        QgsGeometry.fromPolylineXY(
            [
                QgsPointXY(0, 0),
                QgsPointXY(0, 1),
                QgsPointXY(0, 2),
            ]
        )
    )

    gate2 = QgsFeature(layer.fields())
    gate2.setAttributes(["name", False, True])
    gate2.setGeometry(
        QgsGeometry.fromPolylineXY(
            [
                QgsPointXY(5, 5),
                QgsPointXY(10, 10),
            ]
        )
    )

    gate3 = QgsFeature(layer.fields())
    gate3.setAttributes(["name", True, False])
    gate3.setGeometry(
        QgsGeometry.fromPolylineXY(
            [
                QgsPointXY(0.25, 1),
                QgsPointXY(1, 1),
                QgsPointXY(1.5, 0.5),
                QgsPointXY(1.5, 0),
                QgsPointXY(1, -0.5),
            ]
        )
    )

    layer.addFeature(gate1)
    layer.addFeature(gate2)
    layer.addFeature(gate3)

    layer.commitChanges()

    return layer


@pytest.fixture
def qgis_gate_line_layer_wrong_field_type():
    layer = QgsVectorLayer("LineString?crs=EPSG:3067", "Line Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("name", QVariant.String))
    layer.addAttribute(QgsField("counts_negative", QVariant.Bool))
    layer.addAttribute(QgsField("counts_positive", QVariant.Int))

    gate = QgsFeature(layer.fields())
    gate.setAttributes(["name", True, True])
    gate.setGeometry(
        QgsGeometry.fromPolylineXY(
            [
                QgsPointXY(0, 0),
                QgsPointXY(0, 1),
                QgsPointXY(0, 2),
            ]
        )
    )

    layer.addFeature(gate)

    layer.commitChanges()

    return layer
