from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsDistanceArea,
    QgsGeometry,
    QgsUnitTypes,
)

from fvh3t.core.exceptions import InvalidSegmentException

if TYPE_CHECKING:
    from datetime import timedelta

    from fvh3t.core.gate import Gate
    from fvh3t.core.trajectory import TrajectoryNode


class TrajectorySegment:
    """
    Class representing the segment between two
    TrajectoryNodes.
    """

    def __init__(self, node_a: TrajectoryNode, node_b: TrajectoryNode) -> None:
        self.node_a = node_a
        self.node_b = node_b

    def speed(self, crs: QgsCoordinateReferenceSystem) -> float:
        da = QgsDistanceArea()
        da.setSourceCrs(crs, QgsCoordinateTransformContext())

        convert: bool = da.lengthUnits() != QgsUnitTypes.DistanceUnit.DistanceMeters

        distance_m: float = da.measureLine(self.node_b.point, self.node_a.point)
        if convert:
            distance_m = da.convertLengthMeasurement(distance_m, QgsUnitTypes.DistanceUnit.DistanceMeters)

        time_difference: timedelta = self.node_b.timestamp - self.node_a.timestamp
        seconds: float = distance_m / time_difference.total_seconds()

        if seconds > 0:
            meters_per_second = distance_m / seconds

            return round(meters_per_second * 3.6, 2)

        if seconds < 0:
            msg = "Node A must be earlier than node B, timewise!"
            raise InvalidSegmentException(msg)

        return 0.0

    def as_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPolylineXY([self.node_a.point, self.node_b.point])

    def intersects_gate(self, gate: Gate) -> bool:
        return self.as_geometry().intersects(gate.geometry())
