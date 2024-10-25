import pytest
from qgis.core import QgsUnitTypes

from fvh3t.core.trajectory import Trajectory, TrajectoryLayer, TrajectoryNode, TrajectorySegment


def test_trajectory_as_geometry(two_node_trajectory: Trajectory) -> None:
    assert two_node_trajectory.as_geometry().asWkt() == "LineString (0 0, 0 1)"


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


def test_trajectory_average_speed(two_node_trajectory: Trajectory, three_node_trajectory: Trajectory):
    assert two_node_trajectory.average_speed() == 36.0
    assert three_node_trajectory.average_speed() == 36.0


def test_trajectory_maximum_speed(accelerating_three_node_trajectory: Trajectory):
    assert accelerating_three_node_trajectory.maximum_speed() == 96.0


def test_trajectory_length(three_node_trajectory: Trajectory):
    assert three_node_trajectory.length() == 2


def test_trajectory_duration(three_node_trajectory: Trajectory):
    assert three_node_trajectory.duration().total_seconds() == 0.2


def test_trajectory_minimum_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.minimum_size() == (0.49, 0.49, 0.49)


def test_trajectory_maximum_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.maximum_size() == (0.51, 0.51, 0.51)


def test_trajectory_average_size(size_changing_trajectory: Trajectory):
    assert size_changing_trajectory.average_size() == (0.50, 0.50, 0.50)


def test_is_valid_is_layer_valid(qgis_vector_layer):
    with pytest.raises(ValueError, match="Layer is not valid."):
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
    with pytest.raises(ValueError, match="Layer is not a point layer."):
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
    with pytest.raises(ValueError, match="Layer has no features."):
        TrajectoryLayer(
            qgis_point_layer_no_features,
            "id",
            "timestamp",
            "width",
            "length",
            "height",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        )


def test_is_valid_id_field_exists(qgis_point_layer_no_additional_fields):
    with pytest.raises(ValueError, match="Id field not found in the layer."):
        TrajectoryLayer(
            qgis_point_layer_no_additional_fields,
            "id",
            "timestamp",
            "width",
            "length",
            "height",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        )


def test_trajectory_as_segments(two_node_trajectory, three_node_trajectory):
    two_node_segments: tuple[TrajectorySegment, ...] = two_node_trajectory.as_segments()

    assert len(two_node_segments) == 1

    first_seg = two_node_segments[0]

    assert first_seg.node_a.point.x() == 0.0
    assert first_seg.node_a.point.y() == 0.0
    assert first_seg.node_b.point.x() == 0.0
    assert first_seg.node_b.point.y() == 1.0
    assert first_seg.node_a.timestamp.timestamp() == 0.1
    assert first_seg.node_b.timestamp.timestamp() == 0.2

    three_node_segments: tuple[TrajectorySegment, ...] = three_node_trajectory.as_segments()

    assert len(three_node_segments) == 2

    seg1 = three_node_segments[0]
    seg2 = three_node_segments[1]

    assert seg1.node_a.point.x() == 0.0
    assert seg1.node_a.point.y() == 0.0
    assert seg1.node_b.point.x() == 0.0
    assert seg1.node_b.point.y() == 1.0
    assert seg1.node_a.timestamp.timestamp() == 0.1
    assert seg1.node_b.timestamp.timestamp() == 0.2

    assert seg2.node_a.point.x() == 0.0
    assert seg2.node_a.point.y() == 1.0
    assert seg2.node_b.point.x() == 0.0
    assert seg2.node_b.point.y() == 2.0
    assert seg2.node_a.timestamp.timestamp() == 0.2
    assert seg2.node_b.timestamp.timestamp() == 0.3


def test_trajectory_segment_as_geometry(trajectory_segment):
    assert trajectory_segment.as_geometry().asWkt() == "LineString (0 0, 0 1)"
