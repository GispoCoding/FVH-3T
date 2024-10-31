from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsFeature,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterVectorLayer,
    QgsUnitTypes,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication

from fvh3t.core.gate_layer import GateLayer
from fvh3t.core.trajectory_layer import TrajectoryLayer


class CountTrajectories(QgsProcessingAlgorithm):
    INPUT_POINTS = "INPUT_POINTS"
    INPUT_LINES = "INPUT_LINES"
    START_TIME = "START_TIME"
    END_TIME = "END_TIME"
    OUTPUT_GATES = "OUTPUT_GATES"
    OUTPUT_TRAJECTORIES = "OUTPUT_TRAJECTORIES"

    def __init__(self) -> None:
        super().__init__()

        self._name = "count_trajectories"
        self._display_name = "Count trajectories"

    def tr(self, string) -> str:
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):  # noqa N802
        return CountTrajectories()

    def name(self) -> str:
        return self._name

    def displayName(self) -> str:  # noqa N802
        return self.tr(self._display_name)

    def initAlgorithm(self, config=None):  # noqa N802
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INPUT_POINTS,
                description="Input point layer",
                types=[QgsProcessing.TypeVectorPoint],
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INPUT_LINES,
                description="Gates",
                types=[QgsProcessing.TypeVectorLine],
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
                name=self.OUTPUT_GATES,
                description="Gates",
                type=QgsProcessing.TypeVectorLine,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT_TRAJECTORIES,
                description="Trajectories",
                type=QgsProcessing.TypeVectorLine,
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
        start_time = self.parameterAsDateTime(parameters, self.START_TIME, context)
        end_time = self.parameterAsDateTime(parameters, self.END_TIME, context)

        ## CREATE TRAJECTORIES

        feedback.pushInfo(f"Original point layer has {point_layer.featureCount()} features.")

        # Get min and max timestamps from the data
        timestamp_field_id = point_layer.fields().indexOf("timestamp")
        min_timestamp, max_timestamp = point_layer.minimumAndMaximumValue(timestamp_field_id)

        if min_timestamp is None or max_timestamp is None:
            msg = "No valid timestamps found in the point layer."
            raise ValueError(msg)

        # Check if start and end times are empty. If yes, use min and max timestamps. If not, convert to unix time.
        start_time_unix = start_time.toMSecsSinceEpoch() if start_time.isValid() else min_timestamp
        end_time_unix = end_time.toMSecsSinceEpoch() if end_time.isValid() else max_timestamp

        # Check that the set start and end times are in data's range
        if not (min_timestamp <= start_time_unix <= max_timestamp) or not (
            min_timestamp <= end_time_unix <= max_timestamp
        ):
            msg = "Set start and/or end timestamps are out of data's range."
            raise ValueError(msg)

        # Prepare a memory layer for filtered points
        fields = point_layer.fields()
        filtered_layer = QgsVectorLayer("Point?crs=" + point_layer.crs().authid(), "Filtered points", "memory")
        filtered_layer.dataProvider().addAttributes(fields)
        filtered_layer.updateFields()

        id_count = {}
        for feature in point_layer.getFeatures():
            timestamp = feature["timestamp"]
            feature_id = feature["id"]

            # Filter features based on timestamp
            if start_time_unix <= timestamp <= end_time_unix:
                new_feature = QgsFeature(feature)
                filtered_layer.dataProvider().addFeature(new_feature)

                # Count ids
                if feature_id not in id_count:
                    id_count[feature_id] = 0
                id_count[feature_id] += 1

        feedback.pushInfo(f"Filtered {filtered_layer.featureCount()} features based on timestamp range.")

        # Prepare another memory layer for features with non-unique id after filtering time
        non_unique_layer = QgsVectorLayer(
            "Point?crs=" + point_layer.crs().authid(), "Non-unique filtered points", "memory"
        )
        non_unique_layer.dataProvider().addAttributes(fields)
        non_unique_layer.updateFields()

        for feature in filtered_layer.getFeatures():
            feature_id = feature["id"]
            # Add only features with non-unique id
            if id_count.get(feature_id, 0) > 1:
                new_feature = QgsFeature(feature)
                non_unique_layer.dataProvider().addFeature(new_feature)

        feedback.pushInfo(
            f"Final filtered point layer contains {non_unique_layer.featureCount()} features with non-unique IDs."
        )

        trajectory_layer = TrajectoryLayer(
            non_unique_layer,
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
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

        # CREATE GATES
        line_layer = self.parameterAsVectorLayer(parameters, self.INPUT_LINES, context)

        feedback.pushInfo(f"Line layer has {line_layer.featureCount()} features.")

        gate_layer = GateLayer(line_layer, "counts_negative", "counts_positive")

        gates = gate_layer.gates()

        for gate in gates:
            gate.count_trajectories_from_layer(trajectory_layer)

        exported_gate_layer = gate_layer.as_line_layer()

        if exported_gate_layer is None:
            msg = "Gate layer is None"
            raise ValueError(msg)

        (sink, gate_dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_GATES,
            context,
            exported_gate_layer.fields(),
            exported_gate_layer.wkbType(),
            exported_gate_layer.sourceCrs(),
        )

        for feature in exported_gate_layer.getFeatures():
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT_TRAJECTORIES: traj_dest_id, self.OUTPUT_GATES: gate_dest_id}