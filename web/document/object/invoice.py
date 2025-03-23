from itertools import zip_longest

from fpdf import FPDF
from fpdf.enums import TableBordersLayout, XPos, YPos
from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Invoice, Order
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


def gen_invoice_pdf(
    s: Session,
    order: Order,
    invoice: Invoice,
) -> FPDF:
    pdf = FPDF(orientation="portrait", unit="mm", format="A4")
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=30)
    pdf.add_page()

    pdf.image(config.WEBSITE_LOGO_URL, x="L", h=15, keep_aspect_ratio=True)

    pdf.ln(6)
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font(FONT_NAME, "B", size=FONT_SIZE_TITLE)
    pdf.cell(text=_("PDF_INVOICE"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    pdf.ln(6)
    info_data = _get_invoice_info_table_data(s, order, invoice)
    with pdf.table(
        line_height=6,
        text_align=("LEFT", "LEFT", "RIGHT", "LEFT"),
        col_widths=(32, 32, 21, 15),
        borders_layout=TableBordersLayout.NONE,
        first_row_as_headings=False,
    ) as table:
        for info_row in info_data:
            row = table.row()
            for info_value_num, info_value in enumerate(info_row):
                font_style = "B" if info_value_num == 2 else ""
                pdf.set_font(FONT_NAME, font_style, size=FONT_SIZE_NORMAL)
                row.cell(info_value)

    pdf.ln(6)
    pdf.set_font(FONT_NAME, "", size=FONT_SIZE_NORMAL)
    lines_data = _get_invoice_lines_table_data(s, order, invoice)
    with pdf.table(
        line_height=6,
        text_align=("LEFT", "LEFT", "LEFT"),
        col_widths=(70, 15, 15),
        borders_layout=TableBordersLayout.NONE,
        cell_fill_mode=FirstRowFillMode(),
        cell_fill_color=COLOR_DARKGREY,
    ) as table:
        for lines_row_num, lines_row in enumerate(lines_data):
            text_color = COLOR_WHITE if lines_row_num == 0 else COLOR_TEXT
            pdf.set_text_color(*text_color)
            row = table.row()
            for lines_value in lines_row:
                row.cell(lines_value)

    pdf.ln(6)
    pdf.set_text_color(*COLOR_TEXT)
    summary_data = _get_invoice_summary_table_data(s, order, invoice)
    with pdf.table(
        line_height=6,
        text_align=("LEFT", "LEFT"),
        col_widths=(85, 15),
        borders_layout=TableBordersLayout.NONE,
        first_row_as_headings=False,
    ) as table:
        for summary_row in summary_data:
            row = table.row()
            for summary_value_num, summary_value in enumerate(summary_row):
                font_style = "B" if summary_value_num == 0 else ""
                pdf.set_font(FONT_NAME, font_style, size=FONT_SIZE_NORMAL)
                row.cell(summary_value)

    pdf.ln(6)
    pdf.cell(w=0, text=_("PDF_NOTE"), align="R")

    return pdf


def _get_invoice_info_table_data(
    s: Session,
    order: Order,
    invoice: Invoice,
) -> list[tuple[str]]:
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
    ]

    fourth = [
        str(order.id),
        order.created_at.strftime("%Y-%m-%d"),
        invoice.number,
        invoice.created_at.strftime("%Y-%m-%d"),
    ]

    return list(zip_longest(first, second, third, fourth, fillvalue=""))  # type: ignore[arg-type]


def _get_invoice_lines_table_data(
    s: Session,
    order: Order,
    invoice: Invoice,
) -> list[list[str]]:
    data = [[_("PDF_DESCRIPTION"), _("PDF_QUANTITY"), _("PDF_PRICE")]]
    for order_line in order.lines:
        data.append(
            [
                order_line.sku.name,
                str(order_line.quantity),
                f"{format_decimal(order_line.total_price)} {order.currency_code}",
            ]
        )
    return data


def _get_invoice_summary_table_data(
    s: Session,
    order: Order,
    invoice: Invoice,
) -> list[list[str]]:
    return [
        [
            _("PDF_ITEMS"),
            f"{format_decimal(order.subtotal_price)} {order.currency_code}",
        ],
        [
            _("PDF_DISCOUNT"),
            f"{format_decimal(order.discount_price)} {order.currency_code}",
        ],
        [
            _("PDF_SHIPMENT"),
            f"{format_decimal(order.shipment_price)} {order.currency_code}",
        ],
        [
            _("PDF_VAT_PERCENTAGE", vat_percentage=str(order.vat_percentage)),
            f"{format_decimal(order.vat_amount)} {order.currency_code}",
        ],
        [
            _("PDF_TOTAL"),
            f"{format_decimal(order.total_price_vat)} {order.currency_code}",
        ],
    ]
