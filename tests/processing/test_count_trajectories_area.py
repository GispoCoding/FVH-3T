try:
    import processing
except ImportError:
    from qgis import processing

import pytest
from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QDate, QDateTime, QTime, QTimeZone, QVariant

from fvh3t.fvh3t_processing.traffic_trajectory_toolkit_provider import TTTProvider


@pytest.fixture
def input_area_layer_for_algorithm():
    layer = QgsVectorLayer("Polygon?crs=EPSG:3857", "Polygon Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("name", QVariant.String))

    area1 = QgsFeature(layer.fields())
    area1.setAttributes(["area1"])
    area1.setGeometry(
        QgsGeometry.fromPolygonXY(
            [
                [
                    QgsPointXY(1, 2),
                    QgsPointXY(2, 2),
                    QgsPointXY(2, 2.5),
                    QgsPointXY(1, 2.5),
                ],
            ]
        )
    )

    area2 = QgsFeature(layer.fields())
    area2.setAttributes(["area2"])
    area2.setGeometry(
        QgsGeometry.fromPolygonXY(
            [
                [
                    QgsPointXY(0, 0),
                    QgsPointXY(1, 0),
                    QgsPointXY(1, 1),
                    QgsPointXY(0, 1),
                ],
            ]
        )
    )

    layer.addFeature(area1)
    layer.addFeature(area2)

    layer.commitChanges()

    return layer


@pytest.fixture
def input_point_layer_for_algorithm():
    layer = QgsVectorLayer("Point?crs=EPSG:3857", "Point Layer", "memory")

    layer.startEditing()

    layer.addAttribute(QgsField("id", QVariant.Int))
    layer.addAttribute(QgsField("timestamp", QVariant.Double))
    layer.addAttribute(QgsField("size_x", QVariant.Int))
    layer.addAttribute(QgsField("size_y", QVariant.Int))
    layer.addAttribute(QgsField("size_z", QVariant.Int))
    layer.addAttribute(QgsField("label", QVariant.String))

    traj1_f1 = QgsFeature(layer.fields())
    traj1_f1.setAttributes([1, 0, 1, 1, 1, "car"])
    traj1_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, -0.5)))

    traj1_f2 = QgsFeature(layer.fields())
    traj1_f2.setAttributes([1, 1000, 2, 2, 2, "car"])
    traj1_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.25, 0.25)))

    traj1_f3 = QgsFeature(layer.fields())
    traj1_f3.setAttributes([1, 2000, 1, 1, 1, "car"])
    traj1_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.5, 0.5)))

    traj1_f4 = QgsFeature(layer.fields())
    traj1_f4.setAttributes([1, 3000, 2, 2, 2, "car"])
    traj1_f4.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.75, 0.75)))

    traj1_f5 = QgsFeature(layer.fields())
    traj1_f5.setAttributes([1, 4000, 2, 2, 2, "car"])
    traj1_f5.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 1.5)))

    traj2_f1 = QgsFeature(layer.fields())
    traj2_f1.setAttributes([2, 6000000, 1, 1, 1, "car"])
    traj2_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.5, -0.5)))

    traj2_f2 = QgsFeature(layer.fields())
    traj2_f2.setAttributes([2, 6001000, 2, 2, 2, "car"])
    traj2_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.5, 0.25)))

    traj2_f3 = QgsFeature(layer.fields())
    traj2_f3.setAttributes([2, 6002000, 1, 1, 1, "car"])
    traj2_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.5, 0.75)))

    traj2_f4 = QgsFeature(layer.fields())
    traj2_f4.setAttributes([2, 6003000, 2, 2, 2, "car"])
    traj2_f4.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.5, 1.5)))

    traj3_f1 = QgsFeature(layer.fields())
    traj3_f1.setAttributes([3, 6000000, 1, 1, 1, "car"])
    traj3_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0.75, 2.25)))

    traj3_f2 = QgsFeature(layer.fields())
    traj3_f2.setAttributes([3, 6001000, 2, 2, 2, "car"])
    traj3_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.25, 2.25)))

    traj3_f3 = QgsFeature(layer.fields())
    traj3_f3.setAttributes([3, 6002000, 1, 1, 1, "car"])
    traj3_f3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.5, 2.25)))

    traj3_f4 = QgsFeature(layer.fields())
    traj3_f4.setAttributes([3, 6003000, 2, 2, 2, "car"])
    traj3_f4.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.75, 2.25)))

    traj4_f1 = QgsFeature(layer.fields())
    traj4_f1.setAttributes([4, 1000, 1, 1, 1, "pedestrian"])
    traj4_f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.5, 0.5)))

    traj4_f2 = QgsFeature(layer.fields())
    traj4_f2.setAttributes([4, 2000, 2, 2, 2, "pedestrian"])
    traj4_f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.5, 1)))

    layer.addFeature(traj1_f1)
    layer.addFeature(traj1_f2)
    layer.addFeature(traj1_f3)
    layer.addFeature(traj1_f4)
    layer.addFeature(traj1_f5)

    layer.addFeature(traj2_f1)
    layer.addFeature(traj2_f2)
    layer.addFeature(traj2_f3)
    layer.addFeature(traj2_f4)

    layer.addFeature(traj3_f1)
    layer.addFeature(traj3_f2)
    layer.addFeature(traj3_f3)
    layer.addFeature(traj3_f4)

    layer.addFeature(traj4_f1)
    layer.addFeature(traj4_f2)

    layer.commitChanges()

    return layer


def test_count_trajectories_area(
    qgis_app,
    qgis_processing,  # noqa: ARG001
    input_area_layer_for_algorithm: QgsVectorLayer,
    input_point_layer_for_algorithm: QgsVectorLayer,
):
    provider = TTTProvider()

    qgis_app.processingRegistry().addProvider(provider)

    ## TEST CASE 1 - NO FILTERING

    # script requires layers to be added to the project
    QgsProject.instance().addMapLayers([input_area_layer_for_algorithm, input_point_layer_for_algorithm])

    params = {
        "INPUT_POINTS": input_point_layer_for_algorithm,
        "INPUT_AREAS": input_area_layer_for_algorithm,
        "TRAVELER_CLASS": None,
        "START_TIME": None,
        "END_TIME": None,
        "OUTPUT_AREAS": "TEMPORARY_OUTPUT",
        "OUTPUT_TRAJECTORIES": "TEMPORARY_OUTPUT",
    }

    result = processing.run(
        "traffic_trajectory_toolkit:count_trajectories_area",
        params,
    )

    output_areas: QgsVectorLayer = result["OUTPUT_AREAS"]
    output_trajectories: QgsVectorLayer = result["OUTPUT_TRAJECTORIES"]

    assert output_areas.featureCount() == 2
    assert output_trajectories.featureCount() == 3

    area1: QgsFeature = output_areas.getFeature(1)
    area2: QgsFeature = output_areas.getFeature(2)

    assert area1.geometry().asWkt() == "Polygon ((1 2, 2 2, 2 2.5, 1 2.5, 1 2))"
    assert area2.geometry().asWkt() == "Polygon ((0 0, 1 0, 1 1, 0 1, 0 0))"

    assert area1.attribute("vehicle_count") == 1
    assert area2.attribute("vehicle_count") == 2

    assert area1.attribute("speed_avg") == 0.9
    assert round(area2.attribute("speed_avg"), 2) == 1.54

    ### TEST CASE 2 - FILTER BY TIME

    case2_params = {
        "INPUT_POINTS": input_point_layer_for_algorithm,
        "INPUT_AREAS": input_area_layer_for_algorithm,
        "TRAVELER_CLASS": "car",  # filter by class too
        "START_TIME": QDateTime(QDate(1970, 1, 1), QTime(0, 0, 0), QTimeZone.utc()),
        "END_TIME": QDateTime(QDate(1970, 1, 1), QTime(0, 5, 0), QTimeZone.utc()),
        "OUTPUT_AREAS": "TEMPORARY_OUTPUT",
        "OUTPUT_TRAJECTORIES": "TEMPORARY_OUTPUT",
    }

    case2_result = processing.run(
        "traffic_trajectory_toolkit:count_trajectories_area",
        case2_params,
    )

    case2_output_areas: QgsVectorLayer = case2_result["OUTPUT_AREAS"]
    case2_output_trajectories: QgsVectorLayer = case2_result["OUTPUT_TRAJECTORIES"]

    assert case2_output_areas.featureCount() == 2
    assert case2_output_trajectories.featureCount() == 1

    case2area1: QgsFeature = case2_output_areas.getFeature(1)
    case2area2: QgsFeature = case2_output_areas.getFeature(2)

    assert case2area1.attribute("vehicle_count") == 0
    assert case2area2.attribute("vehicle_count") == 1

    traj = case2_output_trajectories.getFeature(1)

    assert traj.geometry().asWkt() == "LineString (0.25 0.25, 0.5 0.5, 0.75 0.75)"

    qgis_app.processingRegistry().removeProvider(provider.id())
