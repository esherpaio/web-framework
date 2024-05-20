import typing
from typing import TYPE_CHECKING

from web.document.base.io.read.types import AnyPDFType
from web.document.base.pdf.canvas.event.end_text_event import EndTextEvent
from web.document.base.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.document.base.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.document.base.pdf.canvas.event.event_listener import EventListener


class EndTextObject(CanvasOperator):
    """End a text object, discarding the text matrix."""

    def __init__(self):
        super().__init__("ET", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the ET operator."""

        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state.text_matrix = None
        canvas.graphics_state.text_line_matrix = None
        for x in event_listeners:
            x._event_occurred(EndTextEvent())
