import typing
from typing import TYPE_CHECKING

from web.pdf.io.read.types import AnyPDFType
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener


class EndCompatibilitySection(CanvasOperator):
    """(PDF 1.1) Begin a compatibility section.

    Unrecognized operators (along with their operands) shall be ignored without error
    until the balancing EX operator is encountered.
    """

    def __init__(self):
        super().__init__("EX", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the EX operator."""

        canvas_stream_processor.get_canvas().in_compatibility_section = False
