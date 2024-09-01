import typing
from typing import TYPE_CHECKING

from web.pdf.io.read.types import AnyPDFType
from web.pdf.io.read.types import Decimal as bDecimal
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener


class MoveToNextLine(CanvasOperator):
    """Move to the start of the next line.

    This operator has the same effect as the code 0 -Tl Td where Tl denotes the current
    leading parameter in the text state. The negative of Tl is used here because Tl is
    the text leading expressed as a positive number. Going to the next line entails
    decreasing the y coordinate.
    """

    def __init__(self):
        super().__init__("T*", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the T* operator."""

        move_text_position_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("Td")
        )
        assert (
            move_text_position_op
        ), "Operator Td must be defined for operator T* to function."
        canvas = canvas_stream_processor.get_canvas()
        move_text_position_op.invoke(
            canvas_stream_processor,
            [bDecimal(0), -canvas.graphics_state.leading],  # type: ignore[list-item]
            event_listeners,
        )
