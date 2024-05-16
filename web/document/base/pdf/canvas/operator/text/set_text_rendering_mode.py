import typing

from doc.io.read.types import AnyPDFType
from doc.pdf.canvas.operator.canvas_operator import CanvasOperator

from web.document.base.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.document.base.pdf.canvas.event.event_listener import EventListener


class SetTextRenderingMode(CanvasOperator):
    """Set the text rendering mode, T mode , to render, which shall be an integer.

    Initial value: 0.
    """

    def __init__(self):
        super().__init__("Tr", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the Tr operator."""

        pass
