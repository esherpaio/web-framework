import typing

from doc.io.read.types import AnyPDFType
from doc.pdf.canvas.event.line_render_event import LineRenderEvent
from doc.pdf.canvas.operator.canvas_operator import CanvasOperator

from web.document.base.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.document.base.pdf.canvas.event.event_listener import EventListener


class StrokePath(CanvasOperator):
    """Stroke the path."""

    def __init__(self):
        super().__init__("S", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the S operator."""

        # get graphic state
        canvas = canvas_stream_processor.get_canvas()
        gs = canvas.graphics_state

        # notify listeners
        for el in event_listeners:
            for listener in gs.path:
                el._event_occurred(LineRenderEvent(gs, listener))

        # clear path
        gs.path = []
