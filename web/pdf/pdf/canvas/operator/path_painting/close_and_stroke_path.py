import typing
from typing import TYPE_CHECKING

from web.pdf.io.read.types import AnyPDFType
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener


class CloseAndStrokePath(CanvasOperator):
    """Close and stroke the path.

    This operator shall have the same effect as the sequence h S.
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

        close_subpath_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("h")
        )
        assert close_subpath_op
        close_subpath_op.invoke(canvas_stream_processor, [], event_listeners)

        stroke_path_op: typing.Optional[CanvasOperator] = (
            canvas_stream_processor.get_operator("S")
        )
        assert stroke_path_op
        stroke_path_op.invoke(canvas_stream_processor, [], event_listeners)
