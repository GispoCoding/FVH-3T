from __future__ import annotations

import json
from typing import Any

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication, QDateTime, QVariant


class ExportToJSON(QgsProcessingAlgorithm):
    INPUT_GATES = "INPUT_GATES"
    OUTPUT_JSON = "OUTPUT_JSON"

    def __init__(self) -> None:
        super().__init__()

        self._name = "export_to_json"
        self._display_name = "Export to JSON"

    def tr(self, string) -> str:
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):  # noqa N802
        return ExportToJSON()

    def name(self) -> str:
        return self._name

    def displayName(self) -> str:  # noqa N802
        return self.tr(self._display_name)

    def initAlgorithm(self, config=None):  # noqa N802
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INPUT_GATES,
                description="Input gates",
                types=[QgsProcessing.TypeVectorLine],
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                name=self.OUTPUT_JSON,
                description="Output JSON file",
                fileFilter="JSON files (*.json)",
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

        gate_layer = self.parameterAsVectorLayer(parameters, self.INPUT_GATES, context)
        output_json_path = self.parameterAsFile(parameters, self.OUTPUT_JSON, context)

        fields_to_exclude = ["fid", "counts_negative", "counts_positive"]

        features_data = []

        for feature in gate_layer.getFeatures():
            feature_dict = {}

            for field_name, field_value in zip(gate_layer.fields().names(), feature.attributes()):
                if field_name not in fields_to_exclude:
                    if field_name in ("vehicle_count_negative", "vehicle_count_positive"):
                        continue

                    if field_name == "name":
                        field_name = "channel"  # noqa: PLW2901

                    # Convert speed km/h -> m/s
                    value = field_value / 3.6 if field_name == "speed_avg" else field_value

                    # Convert QVariant nulls to None
                    if isinstance(field_value, QVariant):
                        value = None if value.isNull() else value.value()

                    # Convert QTime objects to string
                    if isinstance(field_value, QDateTime):
                        value = value.toString("yyyy-MM-dd HH-mm-ss")

                    feature_dict[field_name] = value

            features_data.append(feature_dict)

        with open(output_json_path, "w") as json_file:
            json.dump(features_data, json_file, indent=2)

        return {self.OUTPUT_JSON: output_json_path}
