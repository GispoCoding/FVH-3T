try:
    import processing
except ImportError:
    from qgis import processing

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.core import QgsVectorLayer

from fvh3t.fvh3t_processing.traffic_trajectory_toolkit_provider import TTTProvider
from tests.processing.test_count_trajectories import (  # noqa: F401
    input_gate_layer_for_algorithm,
    input_point_layer_for_algorithm,
)


def test_export_to_json(
    qgis_app,
    qgis_processing,  # noqa: ARG001
    input_point_layer_for_algorithm,  # noqa: F811
    input_gate_layer_for_algorithm,  # noqa: F811
):
    provider = TTTProvider()
    qgis_app.processingRegistry().removeProvider(provider)
    qgis_app.processingRegistry().addProvider(provider)

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

    params = {
        "INPUT_GATES": output_gates,
        "OUTPUT_JSON": "TEMPORARY_OUTPUT",
    }

    result = processing.run(
        "traffic_trajectory_toolkit:export_to_json",
        params,
    )

    output_json = result["OUTPUT_JSON"]

    with open(output_json) as file:
        json_data = json.load(file)

    assert len(json_data) == 3  # Number of gates
    data = json_data[0]
    assert len(data) == 7  # Number of fields per gate

    keys = {"name", "class", "interval_start", "interval_end", "vehicle_count", "speed_avg", "acceleration_avg"}
    assert set(data.keys()) == keys
