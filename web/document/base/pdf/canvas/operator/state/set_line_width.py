import typing
from decimal import Decimal

from doc.io.read.types import AnyPDFType
from doc.pdf.canvas.operator.canvas_operator import CanvasOperator

from web.document.base.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.document.base.pdf.canvas.event.event_listener import EventListener


class SetLineWidth(CanvasOperator):
    """Set the line width in the graphics state (see 8.4.3.2, "Line Width")."""

    def __init__(self):
        super().__init__("w", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the w operator."""

        assert isinstance(operands[0], Decimal), "Operand 0 of w must be a Decimal"
        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state.line_width = operands[0]
