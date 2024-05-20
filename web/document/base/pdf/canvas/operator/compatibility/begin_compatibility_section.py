import typing
from typing import TYPE_CHECKING

from web.document.base.io.read.types import AnyPDFType
from web.document.base.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.document.base.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.document.base.pdf.canvas.event.event_listener import EventListener


class BeginCompatibilitySection(CanvasOperator):
    """(PDF 1.1) Begin a compatibility section.

    Unrecognized operators (along with their operands) shall be ignored without error
    until the balancing EX operator is encountered.
    """

    def __init__(self):
        super().__init__("BX", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the BX operator."""

        canvas_stream_processor.get_canvas().in_compatibility_section = True
