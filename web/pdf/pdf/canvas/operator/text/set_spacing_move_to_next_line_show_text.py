import typing
from typing import TYPE_CHECKING

from web.pdf.io.read.types import AnyPDFType
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener


class SetSpacingMoveToNextLineShowText(CanvasOperator):
    """Move to the next line and show a text string, using a w as the word spacing and
    a c as the character spacing (setting the corresponding parameters in the text
    state).

    a w and a c shall be numbers expressed in unscaled text space units. This operator
    shall have the same effect as this code: aw Tw ac Tc string '
    """

    def __init__(self):
        super().__init__('"', 3)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the " operator."""

        set_word_spacing_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("Tw")
        )
        assert set_word_spacing_op, (
            'Operator Tw must be defined for operator " to function'
        )
        set_word_spacing_op.invoke(
            canvas_stream_processor, [operands[0]], event_listeners
        )

        set_character_spacing_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("Tc")
        )
        assert set_character_spacing_op, (
            'Operator Tc must be defined for operator " to function'
        )
        set_character_spacing_op.invoke(
            canvas_stream_processor, [operands[1]], event_listeners
        )

        move_to_next_line_show_text_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("'")
        )
        assert move_to_next_line_show_text_op, (
            "Operator ' must be defined for operator \" to function"
        )
        move_to_next_line_show_text_op.invoke(
            canvas_stream_processor, [operands[2]], event_listeners
        )
