from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsFeatureRequest,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
    QgsProcessingUtils,
    QgsUnitTypes,
)
from qgis.PyQt.QtCore import QCoreApplication, QDateTime

from fvh3t.core.area_layer import AreaLayer
from fvh3t.core.qgis_layer_utils import QgisLayerUtils
from fvh3t.core.trajectory_layer import TrajectoryLayer
from fvh3t.fvh3t_processing.utils import ProcessingUtils


class CountTrajectoriesArea(QgsProcessingAlgorithm):
    INPUT_POINTS = "INPUT_POINTS"
    INPUT_AREAS = "INPUT_AREAS"
    TRAVELER_CLASS = "TRAVELER_CLASS"
    START_TIME = "START_TIME"
    END_TIME = "END_TIME"
    OUTPUT_AREAS = "OUTPUT_AREAS"
    OUTPUT_TRAJECTORIES = "OUTPUT_TRAJECTORIES"

    area_dest_id: str | None = None

    def __init__(self) -> None:
        super().__init__()

        self._name = "count_trajectories_area"
        self._display_name = "Count trajectories (areas)"

    def tr(self, string) -> str:
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):  # noqa N802
        return CountTrajectoriesArea()

    def name(self) -> str:
        return self._name

    def displayName(self) -> str:  # noqa N802
        return self.tr(self._display_name)

    def initAlgorithm(self, config=None):  # noqa N802
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INPUT_POINTS,
                description="Input point layer",
                types=[QgsProcessing.SourceType.TypeVectorPoint],
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INPUT_AREAS,
                description="Areas",
                types=[QgsProcessing.SourceType.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.TRAVELER_CLASS,
                description="Class of traveler",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                name=self.START_TIME,
                description="Start time",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                name=self.END_TIME,
                description="End time",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT_AREAS,
                description="Areas",
                type=QgsProcessing.SourceType.TypeVectorPolygon,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT_TRAJECTORIES,
                description="Trajectories",
                type=QgsProcessing.SourceType.TypeVectorLine,
            )
        )

    def processAlgorithm(  # noqa N802
        self,
        parameters: dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> dict:
        """
        Here is where the processing itself takes place.
        """

        # Initialize feedback if it is None
        if feedback is None:
            feedback = QgsProcessingFeedback()

        point_layer = self.parameterAsVectorLayer(parameters, self.INPUT_POINTS, context)
        area_vector_layer = self.parameterAsVectorLayer(parameters, self.INPUT_AREAS, context)
        traveler_class = self.parameterAsString(parameters, self.TRAVELER_CLASS, context)
        start_time: QDateTime = self.parameterAsDateTime(parameters, self.START_TIME, context)
        end_time: QDateTime = self.parameterAsDateTime(parameters, self.END_TIME, context)

        # create area layer already so it'll check for validity and terminate if
        # it's invalid
        feedback.pushInfo(f"Area layer has {area_vector_layer.featureCount()} features.")
        area_layer = AreaLayer(area_vector_layer, "name")

        # the datetime widget doesn't allow the user to set the seconds and they
        # are being set seemingly randomly leading to odd results...
        # so set 0 seconds manually
        ProcessingUtils.normalize_datetimes(start_time, end_time)

        ## CREATE TRAJECTORIES

        total_features: int = point_layer.featureCount()
        feedback.pushInfo(f"Original point layer has {total_features} features.")

        # Get min and max timestamps from the data
        min_timestamp, max_timestamp = ProcessingUtils.get_min_and_max_timestamps(point_layer, "timestamp")
        start_time_unix, end_time_unix = ProcessingUtils.get_start_and_end_timestamps(
            start_time, end_time, min_timestamp, max_timestamp
        )

        filter_expression: str | None = ProcessingUtils.get_filter_expression_time_and_class(
            start_time_unix,
            end_time_unix,
            traveler_class,
            min_timestamp,
            max_timestamp,
        )

        if filter_expression is None:
            filter_expression = ""
        else:
            filter_expression += " AND "

        filter_expression += f"(overlay_within('{area_vector_layer.id()}'))"

        req = QgsFeatureRequest().setFilterExpression(filter_expression)
        filtered_points = point_layer.materialize(req)

        total_filtered_points: int = filtered_points.featureCount()
        feedback.pushInfo(f"Filtered {total_features - total_filtered_points} features out.")
        feedback.pushInfo(f"Creating trajectories for {total_filtered_points} points out of {total_features}.")

        trajectory_layer = TrajectoryLayer(
            filtered_points,
            "id",
            "timestamp",
            "size_x",
            "size_y",
            "size_z",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
        )

        exported_traj_layer = trajectory_layer.as_line_layer()

        if exported_traj_layer is None:
            msg = "Trajectory layer is None."
            raise ValueError(msg)

        (sink, traj_dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_TRAJECTORIES,
            context,
            exported_traj_layer.fields(),
            exported_traj_layer.wkbType(),
            exported_traj_layer.sourceCrs(),
        )

        for feature in exported_traj_layer.getFeatures():
            sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)

        # CREATE AREAS

        area_layer.count_trajectories_from_layer(trajectory_layer)

        if not start_time:
            start_time = QDateTime.fromMSecsSinceEpoch(int(min_timestamp))
        if not end_time:
            end_time = QDateTime.fromMSecsSinceEpoch(int(max_timestamp))
        exported_area_layer = area_layer.as_polygon_layer(
            traveler_class=traveler_class, start_time=start_time, end_time=end_time
        )

        if exported_area_layer is None:
            msg = "Polygon layer is None"
            raise ValueError(msg)

        (sink, self.area_dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_AREAS,
            context,
            exported_area_layer.fields(),
            exported_area_layer.wkbType(),
            exported_area_layer.sourceCrs(),
        )

        for feature in exported_area_layer.getFeatures():
            sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)

        return {self.OUTPUT_TRAJECTORIES: traj_dest_id, self.OUTPUT_AREAS: self.area_dest_id}

    def postProcessAlgorithm(self, context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> dict[str, Any]:  # noqa: N802
        if self.area_dest_id:
            layer = QgsProcessingUtils.mapLayerFromString(self.area_dest_id, context)
            QgisLayerUtils.set_area_style(layer)

        return super().postProcessAlgorithm(context, feedback)
