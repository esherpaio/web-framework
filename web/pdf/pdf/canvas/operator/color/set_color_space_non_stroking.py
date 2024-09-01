import typing
from decimal import Decimal
from typing import TYPE_CHECKING, List

from web.pdf.io.read.types import AnyPDFType, Name
from web.pdf.pdf.canvas.color.color import (
    CMYKColor,
    GrayColor,
    RGBColor,
    Separation,
)
from web.pdf.pdf.canvas.operator.canvas_operator import CanvasOperator

if TYPE_CHECKING:
    from web.pdf.pdf.canvas.canvas_stream_processor import (
        CanvasStreamProcessor,
    )
    from web.pdf.pdf.canvas.event.event_listener import EventListener


class SetColorSpaceNonStroking(CanvasOperator):
    """(PDF 1.1) Same as CS but used for nonstroking operations."""

    def __init__(self):
        super().__init__("cs", 1)

    def invoke(
        self,
        canvas_stream_processor: "CanvasStreamProcessor",
        operands: typing.List[AnyPDFType] = [],
        event_listeners: typing.List["EventListener"] = [],
    ) -> None:
        """Invoke the cs operator."""

        assert isinstance(operands[0], Name), "Operand 0 of cs must be a Name"
        color_space_name: Name = operands[0]
        color_space: List = []

        if color_space_name not in [
            "DeviceGray",
            "DeviceRGB",
            "DeviceCMYK",
            "CalGray",
            "CalRGB",
            "Lab",
            "ICCBased",
            "Indexed",
            "Pattern",
            "Separation",
        ]:
            color_space_obj = canvas_stream_processor.get_resource(
                "ColorSpace", color_space_name
            )
            if not isinstance(color_space_name, Name) and isinstance(
                color_space_obj, List
            ):
                color_space = color_space_obj
                color_space_name = color_space_obj[0]

        #
        # Device
        #
        canvas = canvas_stream_processor.get_canvas()
        if color_space_name == "DeviceGray":
            canvas.graphics_state.non_stroke_color_space = color_space_name
            canvas.graphics_state.non_stroke_color = GrayColor(Decimal(0))
            return

        if color_space_name == "DeviceRGB":
            canvas.graphics_state.non_stroke_color_space = color_space_name
            canvas.graphics_state.non_stroke_color = RGBColor(
                Decimal(0), Decimal(0), Decimal(0)
            )
            return

        if color_space_name == "DeviceCMYK":
            canvas.graphics_state.non_stroke_color_space = color_space_name
            canvas.graphics_state.non_stroke_color = CMYKColor(
                Decimal(0), Decimal(0), Decimal(0), Decimal(1)
            )
            return

        #
        # CIE-based
        #

        if color_space_name == "CalGray":
            canvas.graphics_state.non_stroke_color_space = color_space_name
            canvas.graphics_state.non_stroke_color = GrayColor(Decimal(0))
            return

        if color_space_name == "CalRGB":
            canvas.graphics_state.non_stroke_color_space = color_space_name
            canvas.graphics_state.non_stroke_color = RGBColor(
                Decimal(0), Decimal(0), Decimal(0)
            )
            return

        if color_space_name == "Lab":
            canvas.graphics_state.non_stroke_color_space = color_space_name
            return
        if color_space_name == "ICCBased":
            canvas.graphics_state.non_stroke_color_space = color_space_name
            canvas.graphics_state.non_stroke_color = RGBColor(
                Decimal(0), Decimal(0), Decimal(0)
            )
            return

        #
        # Special
        #

        if color_space_name == "Indexed":
            canvas.graphics_state.non_stroke_color_space = color_space_name
            return
        if operands[0] == "Pattern":
            canvas.graphics_state.non_stroke_color_space = operands[0]
            return
        if color_space_name == "Separation":
            canvas.graphics_state.non_stroke_color_space = color_space
            canvas.graphics_state.non_stroke_color = Separation(
                color_space, [Decimal(0)]
            )
