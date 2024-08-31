from decimal import Decimal
from itertools import zip_longest

from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Invoice, Order
from web.i18n import _

from .._utils import float_to_str, save_pdf
from ..base.pdf import (
    Alignment,
    Document,
    FixedColumnWidthTable,
    Image,
    Page,
    SingleColumnLayout,
)
from ..base.toolkit.table.parsing import cells_to_tables
from ..object._style import (
    COLOR_DARKGREY,
    COLOR_LIGHTGREY,
    BoldPG,
    HeadPG,
    TableCell,
    TextPG,
    TitlePG,
)


def gen_invoice(s: Session, order: Order, invoice: Invoice) -> tuple[str, str]:
    pdf = Document()
    page = Page()
    pdf.add_page(page)
    margin = Decimal(30)
    layout = SingleColumnLayout(page, margin, margin)

    image = Image(config.WEBSITE_LOGO_URL, height=Decimal(35))
    image.force_load_image()
    image.set_width_from_height()
    layout.add(image)
    layout.add(TitlePG(_("PDF_INVOICE")))
    layout.add(_build_order_info(order, invoice))

    for num, table in enumerate(_build_order_lines(order)):
        if num > 0:
            page = Page()
            pdf.add_page(page)
            layout = SingleColumnLayout(page, margin, margin)
        layout.add(table)

    pdf_name = _("PDF_INVOICE_FILENAME", invoice_number=invoice.number)
    pdf_path = save_pdf(pdf, pdf_name)
    return pdf_name, pdf_path


def _build_order_info(order: Order, invoice: Invoice) -> FixedColumnWidthTable:
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
    ]

    # Create the table
    row_count = max(len(left_items), len(middle_items), len(right_groups))
    column_widths = [Decimal(4), Decimal(4), Decimal(2), Decimal(2)]
    table = FixedColumnWidthTable(
        number_of_rows=row_count, number_of_columns=4, column_widths=column_widths
    )

    # Append all the rows
    combined = list(zip_longest(left_items, middle_items, right_groups))
    for le, mi, ri in combined:
        if le is not None:
            table.add(le)
        else:
            table.add(TextPG(" "))
        if mi is not None:
            table.add(mi)
        else:
            table.add(TextPG(" "))
        if ri is not None:
            for r_item in ri:
                table.add(r_item)
        else:
            table.add(TextPG(" "))
            table.add(TextPG(" "))

    # Finish the table
    table.set_padding_on_all_cells(Decimal(0), Decimal(2), Decimal(2), Decimal(2))
    table.no_borders()
    return table


def _build_order_lines(order: Order) -> list[FixedColumnWidthTable]:
    cells = []
    h_texts = [_("PDF_DESCRIPTION"), _("PDF_QUANTITY"), _("PDF_PRICE")]
    h_widths = [Decimal(64), Decimal(10), Decimal(16)]
    h_count = len(h_texts)

    # Headers
    for h_text in h_texts:
        h_paragraph = HeadPG(h_text)
        h_cell = TableCell(h_paragraph, background_color=COLOR_DARKGREY)
        cells.append(h_cell)

    # Order lines
    for num, order_line in enumerate(order.lines):
        background_color = COLOR_LIGHTGREY if num % 2 else None
        name_text = f"{order_line.sku.name}"
        name_p = TextPG(name_text)
        cells.append(TableCell(name_p, background_color=background_color))
        quantity_text = f"{order_line.quantity}"
        quantity_p = TextPG(quantity_text)
        cells.append(TableCell(quantity_p, background_color=background_color))
        price_text = f"{float_to_str(order_line.total_price)} {order.currency_code}"
        price_p = TextPG(price_text)
        cells.append(TableCell(price_p, background_color=background_color))

    # Empty line
    empty_p = TextPG(" ")
    cells.append(TableCell(empty_p, col_span=h_count))

    # Subtotal
    subtotal_head_p = BoldPG(_("PDF_ITEMS"))
    subtotal_value_text = f"{float_to_str(order.subtotal_price)} {order.currency_code}"
    subtotal_value_p = TextPG(subtotal_value_text)
    cells.append(TableCell(subtotal_head_p, col_span=h_count - 1))
    cells.append(TableCell(subtotal_value_p, col_span=1))

    # Discount
    subtotal_head_p = BoldPG(_("PDF_DISCOUNT"))
    subtotal_value_text = f"{float_to_str(order.discount_price)} {order.currency_code}"
    subtotal_value_p = TextPG(subtotal_value_text)
    cells.append(TableCell(subtotal_head_p, col_span=h_count - 1))
    cells.append(TableCell(subtotal_value_p, col_span=1))

    # Shipment
    subtotal_head_p = BoldPG(_("PDF_SHIPMENT"))
    subtotal_value_text = f"{float_to_str(order.shipment_price)} {order.currency_code}"
    subtotal_value_p = TextPG(subtotal_value_text)
    cells.append(TableCell(subtotal_head_p, col_span=h_count - 1))
    cells.append(TableCell(subtotal_value_p, col_span=1))

    # VAT
    vat_head_p = BoldPG(
        _("PDF_VAT_PERCENTAGE", vat_percentage=str(order.vat_percentage))
    )
    vat_value_text = f"{float_to_str(order.vat_amount)} {order.currency_code}"
    vat_p = TextPG(vat_value_text)
    cells.append(TableCell(vat_head_p, col_span=h_count - 1))
    cells.append(TableCell(vat_p, col_span=1))

    # Total
    total_head_p = BoldPG(_("PDF_TOTAL"))
    total_value_text = f"{float_to_str(order.total_price_vat)} {order.currency_code}"
    total_value_p = TextPG(total_value_text)
    cells.append(TableCell(total_head_p, col_span=h_count - 1))
    cells.append(TableCell(total_value_p, col_span=1))

    # Empty line
    empty_p = TextPG(" ")
    cells.append(TableCell(empty_p, col_span=h_count))

    # Note
    note_1_text = _("PDF_NOTE")
    note_1_p = TextPG(note_1_text, horizontal_alignment=Alignment.RIGHT)
    cells.append(TableCell(note_1_p, col_span=h_count))

    return cells_to_tables(
        cells,  # type: ignore[arg-type]
        h_count,
        h_widths,
        first_row_count=30,
        other_row_count=42,
        first_top_margin=Decimal(24),
        other_top_margin=Decimal(0),
    )
