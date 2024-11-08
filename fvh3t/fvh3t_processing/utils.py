from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.core import QgsVectorLayer
    from qgis.PyQt.QtCore import QDateTime


class ProcessingUtils:
    @staticmethod
    def get_start_and_end_timestamps(
        start_time: QDateTime,
        end_time: QDateTime,
        min_timestamp: int,
        max_timestamp: int,
    ) -> tuple[int, int]:
        """
        Checks that start and end time are in the correct range
        and returns them as a UNIX timestamp (milliseconds).
        """
        start_time_unix = start_time.toMSecsSinceEpoch() if start_time.isValid() else min_timestamp
        end_time_unix = end_time.toMSecsSinceEpoch() if end_time.isValid() else max_timestamp

        # Check that the set start and end times are in data's range
        if not (min_timestamp <= start_time_unix <= max_timestamp) or not (
            min_timestamp <= end_time_unix <= max_timestamp
        ):
            msg = "Set start and/or end timestamps are out of data's range."
            raise ValueError(msg)

        return start_time_unix, end_time_unix

    @staticmethod
    def get_min_and_max_timestamps(layer: QgsVectorLayer, timestamp_field: str) -> tuple[int, int]:
        field_id = layer.fields().indexOf(timestamp_field)
        min_timestamp, max_timestamp = layer.minimumAndMaximumValue(field_id)

        if min_timestamp is None or max_timestamp is None:
            msg = "No valid timestamps found in the point layer."
            raise ValueError(msg)

        return min_timestamp, max_timestamp

    @staticmethod
    def normalize_datetimes(*args: QDateTime) -> None:
        """
        Sets the seconds to zero in place for all QDateTime objects
        entered into this function.
        """

        for date_time in args:
            zero_s_time = date_time.time()
            zero_s_time.setHMS(zero_s_time.hour(), zero_s_time.minute(), 0)
            date_time.setTime(zero_s_time)

    @staticmethod
    def get_filter_expression_time_and_class(
        start_timestamp: int,
        end_timestamp: int,
        traveler_class: str | None,
        min_timestamp: int,
        max_timestamp: int,
    ) -> str | None:
        """
        Constructs the filter expression from beginning and ending
        time stamps and traveler class, which can be passed
        to TrajectoryLayer.
        """
        filter_expression: str | None = None
        if start_timestamp != min_timestamp or end_timestamp != max_timestamp:
            filter_expression = f'"timestamp" BETWEEN {start_timestamp} AND {end_timestamp}'
        if not filter_expression:
            if traveler_class:
                filter_expression = f"\"label\" = '{traveler_class}'"
        elif traveler_class:
            filter_expression += f" AND \"label\" = '{traveler_class}'"

        return filter_expression
