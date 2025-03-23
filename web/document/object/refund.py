from itertools import zip_longest

from fpdf import FPDF
from fpdf.enums import TableBordersLayout, XPos, YPos
from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Invoice, Order, Refund
from web.i18n import _

from ..style import (
    COLOR_DARKGREY,
    COLOR_TEXT,
    COLOR_WHITE,
    FONT_NAME,
    FONT_SIZE_NORMAL,
    FONT_SIZE_TITLE,
    FirstRowFillMode,
    add_fonts,
)
from ..utils import format_decimal


def gen_refund_pdf(
    s: Session,
    order: Order,
    invoice: Invoice,
    refund: Refund,
) -> FPDF:
    pdf = FPDF(orientation="portrait", unit="mm", format="A4")
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=30)
    pdf.add_page()

    pdf.image(config.WEBSITE_LOGO_URL, x="L", h=15, keep_aspect_ratio=True)

    pdf.ln(6)
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font(FONT_NAME, "B", size=FONT_SIZE_TITLE)
    pdf.cell(text=_("PDF_REFUND"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    pdf.ln(6)
    info_data = _get_refund_info_table_data(s, order, invoice, refund)
    with pdf.table(
        line_height=6,
        text_align=("LEFT", "LEFT", "RIGHT", "LEFT"),
        col_widths=(32, 32, 21, 15),
        borders_layout=TableBordersLayout.NONE,
        first_row_as_headings=False,
    ) as table:
        for data_row in info_data:
            row = table.row()
            for data_value_num, data_value in enumerate(data_row):
                font_style = "B" if data_value_num == 2 else ""
                pdf.set_font(FONT_NAME, font_style, size=FONT_SIZE_NORMAL)
                row.cell(data_value)

    pdf.ln(6)
    pdf.set_font(FONT_NAME, "", size=FONT_SIZE_NORMAL)
    lines_data = _get_refund_lines_table_data(s, order, invoice, refund)
    with pdf.table(
        line_height=6,
        text_align=("LEFT", "LEFT", "LEFT"),
        col_widths=(70, 15, 15),
        borders_layout=TableBordersLayout.NONE,
        cell_fill_mode=FirstRowFillMode(),
        cell_fill_color=COLOR_DARKGREY,
    ) as table:
        for data_row_num, data_row in enumerate(lines_data):
            text_color = COLOR_WHITE if data_row_num == 0 else COLOR_TEXT
            pdf.set_text_color(*text_color)
            row = table.row()
            for data_value in data_row:
                row.cell(data_value)

    pdf.ln(6)
    pdf.set_text_color(*COLOR_TEXT)
    summary_data = _get_refund_summary_table_data(s, order, invoice, refund)
    with pdf.table(
        line_height=6,
        text_align=("LEFT", "LEFT"),
        col_widths=(85, 15),
        borders_layout=TableBordersLayout.NONE,
        first_row_as_headings=False,
    ) as table:
        for data_row in summary_data:
            row = table.row()
            for data_value_num, data_value in enumerate(data_row):
                font_style = "B" if data_value_num == 0 else ""
                pdf.set_font(FONT_NAME, font_style, size=FONT_SIZE_NORMAL)
                row.cell(data_value)

    return pdf


def _get_refund_info_table_data(
    s: Session,
    order: Order,
    invoice: Invoice,
    refund: Refund,
) -> list[list[str]]:
    first = []
    if order.billing.company:
        first.append(order.billing.company)
    first.append(order.billing.full_name)
    first.append(order.billing.address)
    first.append(f"{order.billing.zip_code} {order.billing.city}")
    if order.billing.state:
        first.append(order.billing.state)
    first.append(order.billing.country.name)
    first.append(order.billing.email)

    second = [
        config.BUSINESS_NAME,
        config.BUSINESS_STREET,
        f"{config.BUSINESS_ZIP_CODE} {config.BUSINESS_CITY}",
        config.BUSINESS_COUNTRY,
        _("PDF_CC_NUMBER", cc=config.BUSINESS_CC),
        _("PDF_VAT_NUMBER", vat=config.BUSINESS_VAT),
    ]

    third = [
        _("PDF_ORDER_ID"),
        _("PDF_ORDER_DATE"),
        _("PDF_INVOICE_NUMBER"),
        _("PDF_INVOICE_DATE"),
        _("PDF_REFUND_NUMBER"),
        _("PDF_REFUND_DATE"),
    ]

    fourth = [
        str(order.id),
        order.created_at.strftime("%Y-%m-%d"),
        invoice.number,
        invoice.created_at.strftime("%Y-%m-%d"),
        refund.number,
        refund.created_at.strftime("%Y-%m-%d"),
    ]

    return list(zip_longest(first, second, third, fourth, fillvalue=""))  # type: ignore[arg-type]


def _get_refund_lines_table_data(
    s: Session,
    order: Order,
    invoice: Invoice,
    refund: Refund,
) -> list[list[str]]:
    return [
        [
            _("PDF_DESCRIPTION"),
            _("PDF_QUANTITY"),
            _("PDF_PRICE"),
        ],
        [
            _("PDF_REFUND"),
            str(1),
            f"{format_decimal(refund.total_price)} {order.currency_code}",
        ],
    ]


def _get_refund_summary_table_data(
    s: Session,
    order: Order,
    invoice: Invoice,
    refund: Refund,
) -> list[list[str]]:
    return [
        [
            _("PDF_SUBTOTAL"),
            f"{format_decimal(refund.subtotal_price)} {order.currency_code}",
        ],
        [
            _("PDF_VAT_PERCENTAGE", vat_percentage=str(order.vat_percentage)),
            f"{format_decimal(refund.vat_amount)} {order.currency_code}",
        ],
        [
            _("PDF_TOTAL"),
            f"{format_decimal(refund.total_price_vat)} {order.currency_code}",
        ],
    ]
