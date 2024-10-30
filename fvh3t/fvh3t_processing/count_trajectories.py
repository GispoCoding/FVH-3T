from __future__ import annotations

from typing import Any

from qgis import processing  # noqa: TCH002
from qgis.core import (
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterVectorLayer,
    QgsUnitTypes,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QCoreApplication

from fvh3t.core.trajectory_layer import TrajectoryLayer


class CountTrajectories(QgsProcessingAlgorithm):
    def __init__(self) -> None:
        super().__init__()

        self._name = "create_trajectories"
        self._display_name = "Create trajectories"

    def tr(self, string) -> str:
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):  # noqa N802
        return CountTrajectories()

    def name(self) -> str:
        return self._name

    def displayName(self) -> str:  # noqa N802
        return self.tr(self._display_name)

    def initAlgorithm(self, config=None):  # noqa N802
        self.alg_parameters = [
            "input_point_layer",
            "input_line_layer",
            "start_time",
            "end_time",
            "output_gate_layer",
            "output_trajectory_layer",
        ]

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.alg_parameters[0],
                description="Input point layer",
                types=[QgsProcessing.TypeVectorPoint],
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.alg_parameters[1],
                description="Input line layer",
                types=[QgsProcessing.TypeVectorLine],
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                name=self.alg_parameters[2],
                description="Start time",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                name=self.alg_parameters[3],
                description="End time",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.alg_parameters[4],
                description="Output gate layer",
                type=QgsProcessing.TypeVectorLine,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.alg_parameters[5],
                description="Output trajectory layer",
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

        point_layer = self.parameterAsVectorLayer(parameters, self.alg_parameters[0], context)
        point_layer.fields()

        # line_layer = self.parameterAsSource(parameters, self.alg_parameters[1], context)
        # start_time = self.parameterAsDateTime(parameters, self.alg_parameters[2], context)
        # end_time = self.parameterAsDateTime(parameters, self.alg_parameters[3], context)

        trajectory_layer = TrajectoryLayer(
            point_layer, "id", "timestamp", "size_x", "size_y", "size_z", QgsUnitTypes.TemporalUnit.TemporalMilliseconds
        ).as_line_layer()

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.alg_parameters[5],
            context,
            point_layer.fields(),
            QgsWkbTypes.LineString,
            point_layer.sourceCrs(),
        )

        sink.addFeature(trajectory_layer, QgsFeatureSink.FastInsert)
        # Send some information to the user
        # feedback.pushInfo(f"CRS is {source.sourceCrs().authid()}")

        # # Compute the number of steps to display within the progress bar and
        # # get features from source
        # total = 100.0 / source.featureCount() if source.featureCount() else 0
        # features = source.getFeatures()

        # for current, feature in enumerate(features):
        #     # Stop the algorithm if cancel button has been clicked
        #     if feedback.isCanceled():
        #         break

        #     # Add a feature in the sink
        #     sink.addFeature(feature, QgsFeatureSink.FastInsert)

        #     # Update the progress bar
        #     feedback.setProgress(int(current * total))

        # gate_layer = GateLayer(line_layer, "counts_left", "counts_right")

        # # Send some information to the user
        # feedback.pushInfo(f"CRS is {source.sourceCrs().authid()}")

        # # Compute the number of steps to display within the progress bar and
        # # get features from source
        # total = 100.0 / source.featureCount() if source.featureCount() else 0
        # features = source.getFeatures()

        # for current, feature in enumerate(features):
        #     # Stop the algorithm if cancel button has been clicked
        #     if feedback.isCanceled():
        #         break

        #     # Add a feature in the sink
        #     sink.addFeature(feature, QgsFeatureSink.FastInsert)

        #     # Update the progress bar
        #     feedback.setProgress(int(current * total))

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancellation and progress reports!)
        if False:
            _buffered_layer = processing.run(
                "native:buffer",
                {
                    "INPUT": dest_id,
                    "DISTANCE": 1.5,
                    "SEGMENTS": 5,
                    "END_CAP_STYLE": 0,
                    "JOIN_STYLE": 0,
                    "MITER_LIMIT": 2,
                    "DISSOLVE": False,
                    "OUTPUT": "memory:",
                },
                context=context,
                feedback=feedback,
            )["OUTPUT"]

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}
