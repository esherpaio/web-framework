import typing
from decimal import Decimal
from typing import TYPE_CHECKING

from web.pdf.io.read.types import AnyPDFType
from web.pdf.pdf.canvas.geometry.line_segment import LineSegment
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener


class BeginSubpath(CanvasOperator):
    """Begin a new subpath by moving the current point to coordinates (x, y), omitting
    any connecting line segment.

    If the previous path construction operator in the current path was also m, the new
    m overrides it; no vestige of the previous m operation remains in the path.
    """

    def __init__(self):
        super().__init__("m", 2)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the m operator."""

        assert isinstance(
            operands[0], Decimal
        ), "operand 0 of m operator must be of type Decimal"
        assert isinstance(
            operands[1], Decimal
        ), "operand 1 of m operator must be of type Decimal"

        # get graphic state
        canvas = canvas_stream_processor.get_canvas()
        gs = canvas.graphics_state

        # start empty subpath
        gs.path.append(LineSegment(operands[0], operands[1], operands[0], operands[1]))
