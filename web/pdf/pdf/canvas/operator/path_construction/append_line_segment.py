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


class AppendLineSegment(CanvasOperator):
    """Append a straight line segment from the current point to the point (x, y).

    The new current point shall be (x, y).
    """

    def __init__(self):
        super().__init__("l", 2)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invokes the l operator."""

        assert isinstance(
            operands[0], Decimal
        ), "operand 0 of l operator must be of type Decimal"
        assert isinstance(
            operands[1], Decimal
        ), "operand 1 of l operator must be of type Decimal"

        # get graphic state
        canvas = canvas_stream_processor.get_canvas()
        gs = canvas.graphics_state

        # path should not be empty
        assert len(gs.path) > 0

        # append all paths
        x0 = gs.path[-1].x1
        y0 = gs.path[-1].y1
        gs.path.append(LineSegment(x0, y0, operands[0], operands[1]))
