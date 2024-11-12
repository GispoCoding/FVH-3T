import logging
from typing import TYPE_CHECKING

import pytest
from qgis.core import QgsUnitTypes, QgsVectorLayer

from fvh3t.core.exceptions import InvalidLayerException
from fvh3t.core.trajectory_layer import TrajectoryLayer

if TYPE_CHECKING:
    from fvh3t.core.trajectory import Trajectory, TrajectoryNode


def test_trajectory_layer_create_trajectories(qgis_point_layer):
    traj_layer = TrajectoryLayer(
        qgis_point_layer, "id", "timestamp", "width", "length", "height", QgsUnitTypes.TemporalUnit.TemporalMilliseconds
    )

    trajectories: tuple[Trajectory, ...] = traj_layer.trajectories()
    assert len(trajectories) == 2

    traj1: Trajectory = trajectories[0]
    traj2: Trajectory = trajectories[1]

    assert traj1.as_geometry().asWkt() == "LineString (0 0, 1 0, 2 0)"
    assert traj2.as_geometry().asWkt() == "LineString (5 1, 5 2, 5 3)"

    nodes1: tuple[TrajectoryNode, ...] = traj1.nodes()
    nodes2: tuple[TrajectoryNode, ...] = traj2.nodes()

    assert len(nodes1) == 3
    assert len(nodes2) == 3

    assert nodes1[0].timestamp.timestamp() == 0.1
    assert nodes1[1].timestamp.timestamp() == 0.2
    assert nodes1[2].timestamp.timestamp() == 0.3

    assert nodes2[0].timestamp.timestamp() == 0.5
    assert nodes2[1].timestamp.timestamp() == 0.6
    assert nodes2[2].timestamp.timestamp() == 0.7


def test_trajectory_layer_create_line_layer(qgis_point_layer):
    traj_layer = TrajectoryLayer(
        qgis_point_layer, "id", "timestamp", "width", "length", "height", QgsUnitTypes.TemporalUnit.TemporalMilliseconds
    )

    line_layer = traj_layer.as_line_layer()

    assert line_layer is not None
    assert line_layer.featureCount() == 2
    assert len(line_layer.fields()) == 15

    feat1 = line_layer.getFeature(1)
    feat2 = line_layer.getFeature(2)

    assert feat1.geometry().asWkt() == "LineString (0 0, 1 0, 2 0)"
    assert feat2.geometry().asWkt() == "LineString (5 1, 5 2, 5 3)"

    assert feat1.attribute("average_speed") == 36.0
    assert feat2.attribute("average_speed") == 36.0


def test_trajectory_layer_node_ordering(qgis_point_layer_non_ordered):
    traj_layer = TrajectoryLayer(
        qgis_point_layer_non_ordered,
        "id",
        "timestamp",
        "width",
        "length",
        "height",
        QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
    )

    trajectories = traj_layer.trajectories()

    assert len(trajectories) == 1

    nodes = trajectories[0].nodes()

    assert len(nodes) == 3

    assert nodes[0].timestamp.timestamp() == 1.0
    assert nodes[1].timestamp.timestamp() == 3.0
    assert nodes[2].timestamp.timestamp() == 6.0


def test_is_valid_is_layer_valid(qgis_vector_layer):
    with pytest.raises(InvalidLayerException, match="Layer is not valid."):
        TrajectoryLayer(
            qgis_vector_layer,
            "id",
            "timestamp",
            "width",
            "length",
            "height",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        )


def test_is_valid_is_point_layer(qgis_line_layer):
    with pytest.raises(InvalidLayerException, match="Layer is not a point layer."):
        TrajectoryLayer(
            qgis_line_layer,
            "id",
            "timestamp",
            "width",
            "length",
            "height",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        )


def test_is_valid_has_features(qgis_point_layer_no_features):
    with pytest.raises(InvalidLayerException, match="Layer has no features."):
        TrajectoryLayer(
            qgis_point_layer_no_features,
            "id",
            "timestamp",
            "width",
            "length",
            "height",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        )


def test_is_field_valid(qgis_point_layer_no_additional_fields, qgis_point_layer_wrong_type):
    with pytest.raises(InvalidLayerException, match="Id field either not found or of incorrect type."):
        TrajectoryLayer(
            qgis_point_layer_no_additional_fields,
            "id",
            "timestamp",
            "width",
            "length",
            "height",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        )

    with pytest.raises(InvalidLayerException, match="Timestamp field either not found or of incorrect type."):
        TrajectoryLayer(
            qgis_point_layer_wrong_type,
            "id",
            "timestamp",
            "width",
            "length",
            "height",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        )


def test_create_trajectory_layer_extra_filter_expression(qgis_point_layer: QgsVectorLayer):
    filter_expression = '"timestamp" BETWEEN 200 AND 600'

    layer = TrajectoryLayer(
        qgis_point_layer,
        "id",
        "timestamp",
        "width",
        "length",
        "height",
        QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        filter_expression,
    )

    trajectories = layer.trajectories()

    assert len(trajectories) == 2

    traj1 = trajectories[0]
    traj2 = trajectories[1]

    traj1nodes = traj1.nodes()
    traj2nodes = traj2.nodes()

    assert len(traj1nodes) == 2
    assert len(traj2nodes) == 2

    assert traj1nodes[0].timestamp.timestamp() == 0.2
    assert traj1nodes[1].timestamp.timestamp() == 0.3

    assert traj2nodes[0].timestamp.timestamp() == 0.5
    assert traj2nodes[1].timestamp.timestamp() == 0.6


def test_create_trajectory_layer_single_trajectory_node(qgis_single_point_layer, caplog):
    caplog.set_level(logging.INFO)

    layer = TrajectoryLayer(
        qgis_single_point_layer,
        "id",
        "timestamp",
        "width",
        "length",
        "height",
        QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
    )

    assert len(layer.trajectories()) == 0
    assert 'Trajectory with id "1" has only one node, skipping...' in caplog.text
