import typing

from doc.io.read.types import AnyPDFType
from doc.pdf.canvas.event.begin_text_event import BeginTextEvent
from doc.pdf.canvas.geometry.matrix import Matrix
from doc.pdf.canvas.operator.canvas_operator import CanvasOperator

from web.document.base.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.document.base.pdf.canvas.event.event_listener import EventListener


class BeginTextObject(CanvasOperator):
    """Begin a text object, initializing the text matrix, Tm , and the text line
    matrix, Tlm , to the identity matrix.

    Text objects shall not be nested; a second BT shall not appear before an ET.
    """

    def __init__(self):
        super().__init__("BT", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the BT operator."""

        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state.text_matrix = Matrix.identity_matrix()
        canvas.graphics_state.text_line_matrix = Matrix.identity_matrix()
        for x in event_listeners:
            x._event_occurred(BeginTextEvent())
