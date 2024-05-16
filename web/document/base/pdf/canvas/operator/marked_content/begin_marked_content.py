import typing

from web.document.base.io.read.types import AnyPDFType, Name
from web.document.base.pdf.canvas.operator.canvas_operator import CanvasOperator


class BeginMarkedContent(CanvasOperator):
    """Begin a marked-content sequence terminated by a balancing EMC operator.

    tag shall be a name object indicating the role or significance of the sequence.
    """

    def __init__(self):
        super().__init__("BMC", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the BMC operator."""

        assert isinstance(operands[0], Name), "Operand 0 of BMC must be a Name"
        canvas = canvas_stream_processor.get_canvas()
        canvas.marked_content_stack.append(operands[0])
