import typing
from decimal import Decimal
from typing import TYPE_CHECKING

from web.pdf.io.read.types import AnyPDFType
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener


class SetWordSpacing(CanvasOperator):
    """Set the word spacing, T w , to wordSpace, which shall be a number expressed in
    unscaled text space units.

    Word spacing shall be used by the Tj, TJ, and ' operators. Initial value: 0.
    """

    def __init__(self):
        super().__init__("Tw", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the Tw operator."""

        assert isinstance(operands[0], Decimal)
        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state.word_spacing = operands[0]
