from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
    QgsUnitTypes,
)
from qgis.PyQt.QtCore import QCoreApplication, QDateTime

from fvh3t.core.gate_layer import GateLayer
from fvh3t.core.trajectory_layer import TrajectoryLayer


class CountTrajectories(QgsProcessingAlgorithm):
    INPUT_POINTS = "INPUT_POINTS"
    INPUT_LINES = "INPUT_LINES"
    TRAVELER_CLASS = "TRAVELER_CLASS"
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
        traveler_class = self.parameterAsString(parameters, self.TRAVELER_CLASS, context)
        start_time: QDateTime = self.parameterAsDateTime(parameters, self.START_TIME, context)
        end_time: QDateTime = self.parameterAsDateTime(parameters, self.END_TIME, context)

        # the datetime widget doesn't allow the user to set the seconds and they
        # are being set seemingly randomly leading to odd results...
        # so set 0 seconds manually

        zero_s_start_time = start_time.time()
        zero_s_start_time.setHMS(zero_s_start_time.hour(), zero_s_start_time.minute(), 0)
        start_time.setTime(zero_s_start_time)

        zero_s_end_time = end_time.time()
        zero_s_end_time.setHMS(zero_s_end_time.hour(), zero_s_end_time.minute(), 0)
        end_time.setTime(zero_s_end_time)

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

        # If start or end time was given, filter the nodes outside the time range
        filter_expression: str | None = None
        if start_time_unix != min_timestamp or end_time_unix != max_timestamp:
            filter_expression = f'"timestamp" BETWEEN {start_time_unix} AND {end_time_unix}'
        if not filter_expression:
            if traveler_class:
                filter_expression = f"\"label\" = '{traveler_class}'"
        elif traveler_class:
            filter_expression += f" AND \"label\" = '{traveler_class}'"

        trajectory_layer = TrajectoryLayer(
            point_layer,
            "id",
            "timestamp",
            "size_x",
            "size_y",
            "size_z",
            QgsUnitTypes.TemporalUnit.TemporalMilliseconds,
            filter_expression,
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

        gate_layer = GateLayer(line_layer, "name", "counts_negative", "counts_positive")

        gates = gate_layer.gates()

        for gate in gates:
            gate.count_trajectories_from_layer(trajectory_layer)

        exported_gate_layer = gate_layer.as_line_layer(
            traveler_class=traveler_class, start_time=start_time, end_time=end_time
        )

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

        return {self.OUTPUT_TRAJECTORIES: traj_dest_id, self.OUTPUT_GATES: gate_dest_id}
