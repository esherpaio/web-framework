from decimal import Decimal

from doc.pdf import HexColor
from doc.pdf import Paragraph as Paragraph_
from doc.pdf import TableCell as TableCell_
from doc.pdf.canvas.layout.layout_element import LayoutElement

FONT_NORMAL = "Helvetica"
FONT_BOLD = "Helvetica Bold"
FONT_SIZE_NORMAL = Decimal(10)
FONT_SIZE_TITLE = Decimal(18)
FONT_COLOR = HexColor("444444")


class Paragraph(Paragraph_):
    def __init__(
        self,
        text: str,
        font: str = FONT_NORMAL,
        font_size: Decimal = FONT_SIZE_NORMAL,
        color: HexColor = FONT_COLOR,
        **kwargs,
    ) -> None:
        super().__init__(
            text,
            font=font,
            font_size=font_size,
            font_color=color,
            **kwargs,
        )


class TableCell(TableCell_):
    def __init__(
        self,
        element: LayoutElement,
        background_color: HexColor = HexColor("ffffff"),
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
