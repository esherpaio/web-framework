import os

from fpdf import FPDF

from ._utils import DIR

FONT_NAME = "NotoSans"
FONT_SIZE_NORMAL = 10
FONT_SIZE_TITLE = 18

COLOR_TEXT = (68, 68, 68)
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHTGREY = (240, 240, 240)
COLOR_DARKGREY = (100, 100, 100)


def add_fonts(pdf: FPDF) -> None:
    normal_font_path = os.path.join(DIR, "font", "notosans-regular.ttf")
    bold_font_path = os.path.join(DIR, "font", "notosans-semibold.ttf")
    pdf.add_font(FONT_NAME, "", normal_font_path)
    pdf.add_font(FONT_NAME, "B", bold_font_path)


class FirstRowFillMode:
    @staticmethod
    def should_fill_cell(i: int, j: int) -> bool:
        return i == 0
