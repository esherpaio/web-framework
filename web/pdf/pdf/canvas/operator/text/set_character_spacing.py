import typing
from decimal import Decimal
from typing import TYPE_CHECKING

from web.pdf.io.read.types import AnyPDFType

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator


class SetCharacterSpacing(CanvasOperator):
    """Set the character spacing, Tc , to charSpace, which shall be a number expressed
    in unscaled text space units.

    Character spacing shall be used by the Tj, TJ, and ' operators. Initial value: 0.
    """

    def __init__(self):
        super().__init__("Tc", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the Tc operator."""

        assert isinstance(operands[0], Decimal), "Operand 0 of Tc must be a Decimal"
        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state.character_spacing = operands[0]
