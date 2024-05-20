import typing
from typing import TYPE_CHECKING

from web.document.base.io.read.types import AnyPDFType, Decimal, Name
from web.document.base.pdf.canvas.font.font import Font

if TYPE_CHECKING:
    from web.document.base.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.document.base.pdf.canvas.event.event_listener import EventListener
    from web.document.base.pdf.canvas.font.font import Font
from web.document.base.pdf.canvas.operator.canvas_operator import CanvasOperator


class SetFontAndSize(CanvasOperator):
    """Set the text font, T f , to font and the text font size, T fs , to size.

    font shall be the name of a font resource in the Font subdictionary of the current
    resource dictionary; size shall be a number representing a scale factor. There is
    no initial value for either font or size; they shall be specified explicitly by
    using Tf before any text is shown.
    """

    def __init__(self):
        super().__init__("Tf", 2)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the Tf operator."""

        # lookup font dictionary
        assert isinstance(operands[0], (Name, str))
        font_ref = canvas_stream_processor.get_resource("Font", operands[0])
        assert font_ref is not None
        assert isinstance(font_ref, Font)

        # font size
        assert isinstance(operands[1], Decimal)
        font_size = operands[1]

        # set state
        canvas = canvas_stream_processor.get_canvas()
        canvas.graphics_state.font_size = font_size
        assert isinstance(operands[0], (Name, Font))
        canvas.graphics_state.font = operands[0]
