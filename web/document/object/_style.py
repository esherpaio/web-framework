from decimal import Decimal

from ..base.pdf import HexColor
from ..base.pdf import Paragraph as Paragraph_
from ..base.pdf import TableCell as TableCell_
from ..base.pdf.canvas.layout.layout_element import LayoutElement
from ..base.pdf.canvas.font.simple_font import true_type_font_from_file

FONT_NORMAL = true_type_font_from_file("ttf/notosans-regular.ttf")
FONT_BOLD = true_type_font_from_file("ttf/notosans-semibold.ttf")
# FONT_NORMAL = "Helvetica"
# FONT_BOLD = "Helvetica Bold"
FONT_SIZE_NORMAL = Decimal(10)
FONT_SIZE_TITLE = Decimal(18)
COLOR_TEXT = HexColor("444444")
COLOR_WHITE = HexColor("ffffff")
COLOR_LIGHTGREY = HexColor("f0f0f0")
COLOR_DARKGREY = HexColor("646464")


class TitlePG(Paragraph_):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(
            text,
            font=FONT_BOLD,
            font_size=FONT_SIZE_TITLE,
            font_color=COLOR_TEXT,
            **kwargs,
        )


class TextPG(Paragraph_):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(
            text,
            font=FONT_NORMAL,
            font_size=FONT_SIZE_NORMAL,
            font_color=COLOR_TEXT,
            **kwargs,
        )


class BoldPG(Paragraph_):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(
            text,
            font=FONT_BOLD,
            font_size=FONT_SIZE_NORMAL,
            font_color=COLOR_TEXT,
            **kwargs,
        )


class HeadPG(Paragraph_):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(
            text,
            font=FONT_NORMAL,
            font_size=FONT_SIZE_NORMAL,
            font_color=COLOR_WHITE,
            **kwargs,
        )


class TableCell(TableCell_):
    def __init__(
        self,
        element: LayoutElement,
        background_color: HexColor | None = COLOR_WHITE,
        **kwargs,
    ) -> None:
        super().__init__(
            element,
            background_color=background_color,
            padding_left=Decimal(4),
            padding_right=Decimal(4),
            padding_top=Decimal(4),
            padding_bottom=Decimal(2),
            **kwargs,
        )
