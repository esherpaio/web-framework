from decimal import Decimal
from itertools import zip_longest

from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Invoice, Order, Refund
from web.document._utils import parse_price, save_pdf
from web.document.base.pdf import (
    Alignment,
    Document,
    FixedColumnWidthTable,
    Image,
    Page,
    SingleColumnLayout,
)
from web.document.base.toolkit.table.parsing import cells_to_tables
from web.document.object._style import (
    COLOR_DARKGREY,
    COLOR_LIGHTGREY,
    BoldPG,
    HeadPG,
    TableCell,
    TextPG,
    TitlePG,
)
from web.i18n import _


def gen_refund(
    s: Session,
    order: Order,
    invoice: Invoice,
    refund: Refund,
) -> tuple[str, str]:
    pdf = Document()
    page = Page()
    pdf.add_page(page)
    margin = Decimal(30)
    layout = SingleColumnLayout(page, margin, margin)

    image = Image(config.WEBSITE_LOGO_URL, height=Decimal(35))
    image.force_load_image()
    image.set_width_from_height()
    layout.add(image)
    layout.add(TitlePG(_("PDF_REFUND")))
    layout.add(_build_refund_info(order, invoice, refund))

    tables = _build_refund_lines(order, refund)
    for num, table in enumerate(tables):
        if num > 0:
            page = Page()
            pdf.add_page(page)
            layout = SingleColumnLayout(page, margin, margin)
        layout.add(table)

    pdf_name = _("PDF_REFUND_FILENAME", refund_number=refund.number)
    pdf_path = save_pdf(pdf, pdf_name)
    return pdf_name, pdf_path


def _build_refund_info(
    order: Order,
    invoice: Invoice,
    refund: Refund,
) -> FixedColumnWidthTable:
    # Left 1 column
    left_items = []
    if order.billing.company:
        left_items.append(TextPG(order.billing.company))
    left_items.append(TextPG(order.billing.full_name))
    left_items.append(TextPG(order.billing.address))
    left_items.append(TextPG(f"{order.billing.zip_code} {order.billing.city}"))
    if order.billing.state:
        left_items.append(TextPG(order.billing.state))
    left_items.append(TextPG(order.billing.country.name))
    left_items.append(TextPG(order.billing.email))

    # Middle 1 column
    middle_items = [
        TextPG(config.BUSINESS_NAME),
        TextPG(config.BUSINESS_STREET),
        TextPG(f"{config.BUSINESS_ZIP_CODE} {config.BUSINESS_CITY}"),
        TextPG(config.BUSINESS_COUNTRY),
        TextPG(_("PDF_CC_NUMBER", cc=config.BUSINESS_CC)),
        TextPG(_("PDF_VAT_NUMBER", vat=config.BUSINESS_VAT)),
    ]

    # Right 2 columns
    right_groups = [
        [
            BoldPG(_("PDF_ORDER_ID"), horizontal_alignment=Alignment.RIGHT),
            TextPG(str(order.id)),
        ],
        [
            BoldPG(_("PDF_ORDER_DATE"), horizontal_alignment=Alignment.RIGHT),
            TextPG(order.created_at.strftime("%Y-%m-%d")),
        ],
        [
            BoldPG(_("PDF_INVOICE_NUMBER"), horizontal_alignment=Alignment.RIGHT),
            TextPG(invoice.number),
        ],
        [
            BoldPG(_("PDF_INVOICE_DATE"), horizontal_alignment=Alignment.RIGHT),
            TextPG(invoice.created_at.strftime("%Y-%m-%d")),
        ],
        [
            BoldPG(_("PDF_REFUND_NUMBER"), horizontal_alignment=Alignment.RIGHT),
            TextPG(refund.number),
        ],
        [
            BoldPG(_("PDF_REFUND_DATE"), horizontal_alignment=Alignment.RIGHT),
            TextPG(refund.created_at.strftime("%Y-%m-%d")),
        ],
    ]

    # Create the table
    row_count = max(len(left_items), len(middle_items), len(right_groups))
    column_widths = [Decimal(4), Decimal(4), Decimal(2), Decimal(2)]
    table = FixedColumnWidthTable(
        number_of_rows=row_count, number_of_columns=4, column_widths=column_widths
    )

    # Append all the rows
    combined = list(zip_longest(left_items, middle_items, right_groups))
    for l_item, m_item, r_group in combined:
        if l_item is not None:
            table.add(l_item)
        else:
            table.add(TextPG(" "))
        if m_item is not None:
            table.add(m_item)
        else:
            table.add(TextPG(" "))
        if r_group is not None:
            for r_item in r_group:
                table.add(r_item)
        else:
            table.add(TextPG(" "))
            table.add(TextPG(" "))

    # Finish the table
    table.set_padding_on_all_cells(Decimal(0), Decimal(2), Decimal(2), Decimal(2))
    table.no_borders()
    return table


def _build_refund_lines(
    order: Order,
    refund: Refund,
) -> list[FixedColumnWidthTable]:
    cells = []
    h_texts = [_("PDF_DESCRIPTION"), _("PDF_QUANTITY"), _("PDF_PRICE")]
    h_widths = [Decimal(64), Decimal(10), Decimal(16)]
    h_count = len(h_texts)

    # Headers
    for h_text in h_texts:
        h_paragraph = HeadPG(h_text)
        h_cell = TableCell(h_paragraph, background_color=COLOR_DARKGREY)
        cells.append(h_cell)

    # Line
    name_text = _("PDF_REFUND")
    name_p = TextPG(name_text)
    cells.append(TableCell(name_p, COLOR_LIGHTGREY))
    quantity_text = "1"
    quantity_p = TextPG(quantity_text)
    cells.append(TableCell(quantity_p, COLOR_LIGHTGREY))
    price_text = f"{parse_price(refund.total_price)} {order.currency_code}"
    price_p = TextPG(price_text)
    cells.append(TableCell(price_p, COLOR_LIGHTGREY))

    # Empty line
    empty_p = TextPG(" ")
    cells.append(TableCell(empty_p, col_span=h_count))

    # Subtotal
    subtotal_head_p = BoldPG(_("PDF_SUBTOTAL"), horizontal_alignment=Alignment.RIGHT)
    subtotal_value_text = f"{parse_price(refund.subtotal_price)} {order.currency_code}"
    subtotal_value_p = TextPG(subtotal_value_text)
    cells.append(TableCell(subtotal_head_p, col_span=h_count - 1))
    cells.append(TableCell(subtotal_value_p, col_span=1))

    # VAT
    vat_head_p = BoldPG(
        _("PDF_VAT_PERCENTAGE", vat_percentage=str(order.vat_percentage)),
        horizontal_alignment=Alignment.RIGHT,
    )
    vat_value_text = f"{parse_price(refund.vat_amount)} {order.currency_code}"
    vat_p = TextPG(vat_value_text)
    cells.append(TableCell(vat_head_p, col_span=h_count - 1))
    cells.append(TableCell(vat_p, col_span=1))

    # Total
    total_head_p = BoldPG(_("PDF_TOTAL"), horizontal_alignment=Alignment.RIGHT)
    total_value_text = f"{parse_price(refund.total_price_vat)} {order.currency_code}"
    total_value_p = TextPG(total_value_text)
    cells.append(TableCell(total_head_p, col_span=h_count - 1))
    cells.append(TableCell(total_value_p, col_span=1))

    return cells_to_tables(
        cells,
        h_count,
        h_widths,
        first_row_count=30,
        other_row_count=43,
        first_top_margin=Decimal(24),
        other_top_margin=Decimal(0),
    )
