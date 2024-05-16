import typing
from decimal import Decimal

from doc.io.read.types import AnyPDFType
from doc.pdf.canvas.operator.canvas_operator import CanvasOperator

from web.document.base.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.document.base.pdf.canvas.event.event_listener import EventListener


class SetHorizontalScaling(CanvasOperator):
    """Set the horizontal scaling, Th , to (scale ÷ 100).

    scale shall be a number specifying the percentage of the normal width. Initial
    value: 100 (normal width).
    """

    def __init__(self):
        super().__init__("Tz", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the Tz operator."""

        assert isinstance(operands[0], Decimal), "Operand 0 of Tz must be a Decimal"
        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state.horizontal_scaling = operands[0]
