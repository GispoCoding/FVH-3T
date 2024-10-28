from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.core import QgsGeometry

if TYPE_CHECKING:
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

    def as_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPolylineXY([self.node_a.point, self.node_b.point])

    def intersects_gate(self, gate: Gate) -> bool:
        return self.as_geometry().intersects(gate.geometry())
