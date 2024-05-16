import typing

from web.document.base.io.read.types import AnyPDFType
from web.document.base.pdf.canvas.operator.canvas_operator import CanvasOperator


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
