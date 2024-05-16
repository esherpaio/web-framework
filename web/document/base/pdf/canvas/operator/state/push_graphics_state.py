import copy
import typing

from doc.io.read.types import AnyPDFType
from doc.pdf.canvas.operator.canvas_operator import CanvasOperator

from web.document.base.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.document.base.pdf.canvas.event.event_listener import EventListener


class PushGraphicsState(CanvasOperator):
    """
    Save the current graphics state on the graphics state stack (see
    8.4.2, "Graphics State Stack").
    """

    def __init__(self):
        super().__init__("q", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the q operator."""

        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state_stack.append(copy.deepcopy(canvas.graphics_state))
