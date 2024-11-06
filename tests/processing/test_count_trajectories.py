try:
    import processing
except ImportError:
    from qgis import processing

import pytest
from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer
from qgis.PyQt.QtCore import QDate, QDateTime, QTime, QTimeZone, QVariant

from fvh3t.fvh3t_processing.traffic_trajectory_toolkit_provider import TTTProvider


@pytest.fixture
def input_gate_layer_for_algorithm():
    layer = QgsVectorLayer("LineString?crs=EPSG:3067", "Line Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("name", QVariant.String))
    layer.addAttribute(QgsField("counts_negative", QVariant.Bool))
    layer.addAttribute(QgsField("counts_positive", QVariant.Bool))

    gate1 = QgsFeature(layer.fields())
    gate1.setAttributes(["gate1", True, False])
    gate1.setGeometry(
        QgsGeometry.fromPolylineXY(
            [
                QgsPointXY(0, 0),
                QgsPointXY(1, 0),
            ]
        )
    )

    gate2 = QgsFeature(layer.fields())
    gate2.setAttributes(["gate2", False, True])
    gate2.setGeometry(
        QgsGeometry.fromPolylineXY(
            [
                QgsPointXY(0, 1),
                QgsPointXY(0, 2),
            ]
        )
    )

    gate3 = QgsFeature(layer.fields())
    gate3.setAttributes(["gate3", True, True])
    gate3.setGeometry(
        QgsGeometry.fromPolylineXY(
            [
                QgsPointXY(1, 1),
                QgsPointXY(2, 1),
                QgsPointXY(2, 2),
            ]
        )
    )

    layer.addFeature(gate1)
    layer.addFeature(gate2)
    layer.addFeature(gate3)

    layer.commitChanges()

    return layer


@pytest.fixture
def input_point_layer_for_algorithm():
    layer = QgsVectorLayer("Point?crs=EPSG:3067", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("id", QVariant.Int))
    layer.addAttribute(QgsField("timestamp", QVariant.Double))
    layer.addAttribute(QgsField("size_x", QVariant.Int))
    layer.addAttribute(QgsField("size_y", QVariant.Int))
    layer.addAttribute(QgsField("size_z", QVariant.Int))
    layer.addAttribute(QgsField("label", QVariant.String))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([1, 0, 1, 1, 1, "car"])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 1.5)))

    traj1_f2 = QgsFeature(layer.fields())
    traj1_f2.setAttributes([1, 1000, 2, 2, 2, "car"])
    traj1_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.5, 1.5)))

    traj1_f3 = QgsFeature(layer.fields())
    traj1_f3.setAttributes([1, 2000, 1, 1, 1, "car"])
    traj1_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-0.5, 1.5)))

    traj1_f4 = QgsFeature(layer.fields())
    traj1_f4.setAttributes([1, 3000, 2, 2, 2, "car"])
    traj1_f4.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-1, 2)))

    traj2_f1 = QgsFeature(layer.fields())
    traj2_f1.setAttributes([2, 0, 1, 1, 1, "car"])
    traj2_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-0.5, 1)))

    traj2_f2 = QgsFeature(layer.fields())
    traj2_f2.setAttributes([2, 1000, 2, 2, 2, "car"])
    traj2_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.5, 2)))

    traj3_f1 = QgsFeature(layer.fields())
    traj3_f1.setAttributes([3, 0, 1, 1, 1, "car"])
    traj3_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.5, 0.5)))

    traj3_f2 = QgsFeature(layer.fields())
    traj3_f2.setAttributes([3, 1000, 2, 2, 2, "car"])
    traj3_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.5, 1.5)))

    traj4_f1 = QgsFeature(layer.fields())
    traj4_f1.setAttributes([4, 301000, 1, 1, 1, "car"])
    traj4_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.5, 2)))

    traj4_f2 = QgsFeature(layer.fields())
    traj4_f2.setAttributes([4, 302000, 2, 2, 2, "car"])
    traj4_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(2.5, 1)))

    traj5_f1 = QgsFeature(layer.fields())
    traj5_f1.setAttributes([5, 305000, 1, 1, 1, "car"])
    traj5_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 0.5)))

    traj5_f2 = QgsFeature(layer.fields())
    traj5_f2.setAttributes([5, 306000, 2, 2, 2, "car"])
    traj5_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, -0.5)))

    traj6_f1 = QgsFeature(layer.fields())
    traj6_f1.setAttributes([6, 309000, 1, 1, 1, "car"])
    traj6_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.5, -0.5)))

    traj6_f2 = QgsFeature(layer.fields())
    traj6_f2.setAttributes([6, 310000, 2, 2, 2, "car"])
    traj6_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0.5)))

    layer.addFeature(traj1_f1)
    layer.addFeature(traj1_f2)
    layer.addFeature(traj1_f3)
    layer.addFeature(traj1_f4)

    layer.addFeature(traj2_f1)
    layer.addFeature(traj2_f2)

    layer.addFeature(traj3_f1)
    layer.addFeature(traj3_f2)

    layer.addFeature(traj4_f1)
    layer.addFeature(traj4_f2)

    layer.addFeature(traj5_f1)
    layer.addFeature(traj5_f2)

    layer.addFeature(traj6_f1)
    layer.addFeature(traj6_f2)

    layer.commitChanges()

    return layer


def test_count_trajectories(
    qgis_app,
    qgis_processing,  # noqa: ARG001
    input_point_layer_for_algorithm: QgsVectorLayer,
    input_gate_layer_for_algorithm: QgsVectorLayer,
):
    provider = TTTProvider()

    qgis_app.processingRegistry().addProvider(provider)

    ## TEST CASE 1 - NO FILTERING

    params = {
        "INPUT_POINTS": input_point_layer_for_algorithm,
        "INPUT_LINES": input_gate_layer_for_algorithm,
        "TRAVELER_CLASS": "car",
        "START_TIME": None,
        "END_TIME": None,
        "OUTPUT_GATES": "TEMPORARY_OUTPUT",
        "OUTPUT_TRAJECTORIES": "TEMPORARY_OUTPUT",
    }

    result = processing.run(
        "traffic_trajectory_toolkit:count_trajectories",
        params,
    )

    output_gates: QgsVectorLayer = result["OUTPUT_GATES"]
    output_trajectories: QgsVectorLayer = result["OUTPUT_TRAJECTORIES"]

    assert output_gates.featureCount() == 3
    assert output_trajectories.featureCount() == 6

    gate1: QgsFeature = output_gates.getFeature(1)
    gate2: QgsFeature = output_gates.getFeature(2)
    gate3: QgsFeature = output_gates.getFeature(3)

    assert gate1.geometry().asWkt() == "LineString (0 0, 1 0)"
    assert gate2.geometry().asWkt() == "LineString (0 1, 0 2)"
    assert gate3.geometry().asWkt() == "LineString (1 1, 2 1, 2 2)"

    assert gate1.attribute("vehicle_count") == 1
    assert gate2.attribute("vehicle_count") == 1
    assert gate3.attribute("vehicle_count") == 2

    traj1: QgsFeature = output_trajectories.getFeature(1)
    traj2: QgsFeature = output_trajectories.getFeature(2)
    traj3: QgsFeature = output_trajectories.getFeature(3)
    traj4: QgsFeature = output_trajectories.getFeature(4)
    traj5: QgsFeature = output_trajectories.getFeature(5)
    traj6: QgsFeature = output_trajectories.getFeature(6)

    assert traj1.geometry().asWkt() == "LineString (1 1.5, 0.5 1.5, -0.5 1.5, -1 2)"
    assert traj2.geometry().asWkt() == "LineString (-0.5 1, 0.5 2)"
    assert traj3.geometry().asWkt() == "LineString (1.5 0.5, 1.5 1.5)"
    assert traj4.geometry().asWkt() == "LineString (1.5 2, 2.5 1)"
    assert traj5.geometry().asWkt() == "LineString (1 0.5, 0 -0.5)"
    assert traj6.geometry().asWkt() == "LineString (0.5 -0.5, 0 0.5)"

    assert traj1.attribute("average_speed") == 2.65
    assert traj1.attribute("maximum_speed") == 3.6
    assert traj1.attribute("length") == 2.21
    assert traj1.attribute("duration") == 3
    assert traj1.attribute("minimum_size_x") == 1
    assert traj1.attribute("minimum_size_y") == 1
    assert traj1.attribute("minimum_size_z") == 1
    assert traj1.attribute("maximum_size_x") == 2
    assert traj1.attribute("maximum_size_y") == 2
    assert traj1.attribute("maximum_size_z") == 2
    assert traj1.attribute("average_size_x") == 1.5
    assert traj1.attribute("average_size_y") == 1.5
    assert traj1.attribute("average_size_z") == 1.5

    assert traj2.attribute("average_speed") == 5.09
    assert traj2.attribute("maximum_speed") == 5.09
    assert traj2.attribute("length") == 1.41
    assert traj2.attribute("duration") == 1
    assert traj2.attribute("minimum_size_x") == 1
    assert traj2.attribute("minimum_size_y") == 1
    assert traj2.attribute("minimum_size_z") == 1
    assert traj2.attribute("maximum_size_x") == 2
    assert traj2.attribute("maximum_size_y") == 2
    assert traj2.attribute("maximum_size_z") == 2
    assert traj2.attribute("average_size_x") == 1.5
    assert traj2.attribute("average_size_y") == 1.5
    assert traj2.attribute("average_size_z") == 1.5

    assert traj3.attribute("average_speed") == 3.6
    assert traj3.attribute("maximum_speed") == 3.6
    assert traj3.attribute("length") == 1
    assert traj3.attribute("duration") == 1
    assert traj3.attribute("minimum_size_x") == 1
    assert traj3.attribute("minimum_size_y") == 1
    assert traj3.attribute("minimum_size_z") == 1
    assert traj3.attribute("maximum_size_x") == 2
    assert traj3.attribute("maximum_size_y") == 2
    assert traj3.attribute("maximum_size_z") == 2
    assert traj3.attribute("average_size_x") == 1.5
    assert traj3.attribute("average_size_y") == 1.5
    assert traj3.attribute("average_size_z") == 1.5

    assert traj4.attribute("average_speed") == 5.09
    assert traj4.attribute("maximum_speed") == 5.09
    assert traj4.attribute("length") == 1.41
    assert traj4.attribute("duration") == 1
    assert traj4.attribute("minimum_size_x") == 1
    assert traj4.attribute("minimum_size_y") == 1
    assert traj4.attribute("minimum_size_z") == 1
    assert traj4.attribute("maximum_size_x") == 2
    assert traj4.attribute("maximum_size_y") == 2
    assert traj4.attribute("maximum_size_z") == 2
    assert traj4.attribute("average_size_x") == 1.5
    assert traj4.attribute("average_size_y") == 1.5
    assert traj4.attribute("average_size_z") == 1.5

    assert traj5.attribute("average_speed") == 5.09
    assert traj5.attribute("maximum_speed") == 5.09
    assert traj5.attribute("length") == 1.41
    assert traj5.attribute("duration") == 1
    assert traj5.attribute("minimum_size_x") == 1
    assert traj5.attribute("minimum_size_y") == 1
    assert traj5.attribute("minimum_size_z") == 1
    assert traj5.attribute("maximum_size_x") == 2
    assert traj5.attribute("maximum_size_y") == 2
    assert traj5.attribute("maximum_size_z") == 2
    assert traj5.attribute("average_size_x") == 1.5
    assert traj5.attribute("average_size_y") == 1.5
    assert traj5.attribute("average_size_z") == 1.5

    assert traj6.attribute("average_speed") == 4.02
    assert traj6.attribute("maximum_speed") == 4.02
    assert traj6.attribute("length") == 1.12
    assert traj6.attribute("duration") == 1
    assert traj6.attribute("minimum_size_x") == 1
    assert traj6.attribute("minimum_size_y") == 1
    assert traj6.attribute("minimum_size_z") == 1
    assert traj6.attribute("maximum_size_x") == 2
    assert traj6.attribute("maximum_size_y") == 2
    assert traj6.attribute("maximum_size_z") == 2
    assert traj6.attribute("average_size_x") == 1.5
    assert traj6.attribute("average_size_y") == 1.5
    assert traj6.attribute("average_size_z") == 1.5

    ### TEST CASE 2 - FILTER BY TIME

    case2_params = {
        "INPUT_POINTS": input_point_layer_for_algorithm,
        "INPUT_LINES": input_gate_layer_for_algorithm,
        "TRAVELER_CLASS": "car",
        "START_TIME": QDateTime(QDate(1970, 1, 1), QTime(0, 0, 0), QTimeZone.utc()),
        "END_TIME": QDateTime(QDate(1970, 1, 1), QTime(0, 5, 0), QTimeZone.utc()),
        "OUTPUT_GATES": "TEMPORARY_OUTPUT",
        "OUTPUT_TRAJECTORIES": "TEMPORARY_OUTPUT",
    }

    case2_result = processing.run(
        "traffic_trajectory_toolkit:count_trajectories",
        case2_params,
    )

    case2_output_gates: QgsVectorLayer = case2_result["OUTPUT_GATES"]
    case2_output_trajectories: QgsVectorLayer = case2_result["OUTPUT_TRAJECTORIES"]

    assert case2_output_gates.featureCount() == 3
    assert case2_output_trajectories.featureCount() == 3

    case2gate1: QgsFeature = case2_output_gates.getFeature(1)
    case2gate2: QgsFeature = case2_output_gates.getFeature(2)
    case2gate3: QgsFeature = case2_output_gates.getFeature(3)

    assert case2gate1.geometry().asWkt() == "LineString (0 0, 1 0)"
    assert case2gate2.geometry().asWkt() == "LineString (0 1, 0 2)"
    assert case2gate3.geometry().asWkt() == "LineString (1 1, 2 1, 2 2)"

    assert case2gate1.attribute("vehicle_count") == 0
    assert case2gate2.attribute("vehicle_count") == 1
    assert case2gate3.attribute("vehicle_count") == 1

    case2traj1: QgsFeature = case2_output_trajectories.getFeature(1)
    case2traj2: QgsFeature = case2_output_trajectories.getFeature(2)
    case2traj3: QgsFeature = case2_output_trajectories.getFeature(3)

    assert case2traj1.geometry().asWkt() == "LineString (1 1.5, 0.5 1.5, -0.5 1.5, -1 2)"
    assert case2traj2.geometry().asWkt() == "LineString (-0.5 1, 0.5 2)"
    assert case2traj3.geometry().asWkt() == "LineString (1.5 0.5, 1.5 1.5)"
