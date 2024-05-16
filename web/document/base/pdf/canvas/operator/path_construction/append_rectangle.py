import typing
from decimal import Decimal

from doc.io.read.types import AnyPDFType
from doc.io.read.types import Decimal as bDecimal
from doc.pdf.canvas.operator.canvas_operator import CanvasOperator

from web.document.base.pdf.canvas.canvas_stream_processor import CanvasStreamProcessor
from web.document.base.pdf.canvas.event.event_listener import EventListener


class AppendRectangle(CanvasOperator):
    """Append a rectangle to the current path as a complete subpath, with lower-left
    corner (x, y) and dimensions width and height in user space.

    The operation x y width height re is equivalent to x y m ( x + width ) y l ( x +
    width ) ( y + height ) l x ( y + height ) l h
    """

    def __init__(self):
        super().__init__("s", 0)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the s operator."""

        assert isinstance(operands[0], Decimal)
        assert isinstance(operands[1], Decimal)
        assert isinstance(operands[2], Decimal)
        assert isinstance(operands[3], Decimal)
        x: Decimal = operands[0]
        y: Decimal = operands[1]
        width: Decimal = operands[2]
        height: Decimal = operands[3]

        moveto_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("m")
        )
        assert moveto_op is not None
        moveto_op.invoke(
            canvas_stream_processor, [bDecimal(x), bDecimal(y)], event_listeners
        )

        line_to_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("l")
        )
        assert line_to_op is not None
        line_to_op.invoke(
            canvas_stream_processor, [bDecimal(x + width), bDecimal(y)], event_listeners
        )
        line_to_op.invoke(
            canvas_stream_processor,
            [bDecimal(x + width), bDecimal(y + height)],
            event_listeners,
        )
        line_to_op.invoke(
            canvas_stream_processor,
            [bDecimal(x), bDecimal(y + height)],
            event_listeners,
        )

        close_subpath_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("h")
        )
        assert close_subpath_op is not None
        close_subpath_op.invoke(canvas_stream_processor, [], event_listeners)
