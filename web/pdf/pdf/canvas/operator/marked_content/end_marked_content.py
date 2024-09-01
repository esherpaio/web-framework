import typing
from typing import TYPE_CHECKING

from web.pdf.io.read.types import AnyPDFType
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener


class EndMarkedContent(CanvasOperator):
    """End a marked-content sequence begun by a BMC or BDC operator."""

    def __init__(self):
        super().__init__("EMC", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the EMC operator."""

        canvas = canvas_stream_processor.get_canvas()
        assert len(canvas.marked_content_stack) > 0
        canvas.marked_content_stack.pop(-1)
