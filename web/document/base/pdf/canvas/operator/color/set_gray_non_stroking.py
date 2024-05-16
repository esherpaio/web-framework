import typing
from decimal import Decimal

from doc.io.read.types import AnyPDFType
from doc.pdf.canvas.color.color import GrayColor
from doc.pdf.canvas.operator.canvas_operator import CanvasOperator

from web.document.base.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.document.base.pdf.canvas.event.event_listener import EventListener


class SetGrayNonStroking(CanvasOperator):
    """Same as G but used for nonstroking operations."""

    def __init__(self):
        super().__init__("g", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the g operator."""

        assert isinstance(operands[0], Decimal), "Operand 0 of g must be a Decimal"
        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state.non_stroke_color = GrayColor(operands[0])
