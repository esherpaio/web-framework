from decimal import Decimal
from itertools import zip_longest

from doc.pdf import (
    Alignment,
    Document,
    FixedColumnWidthTable,
    HexColor,
    Image,
    Page,
    SingleColumnLayout,
)

from web import config
from web.database.model import Invoice, Order, Refund
from web.document._base import FONT_BOLD, FONT_SIZE_TITLE, Paragraph, TableCell
from web.document._utils import cells_to_tables, num_to_str, save_pdf

# Todo: add translations


def gen_refund(order: Order, invoice: Invoice, refund: Refund) -> tuple[str, str]:
    pdf = Document()
    page = Page()
    pdf.add_page(page)
    margin = Decimal(30)
    layout = SingleColumnLayout(page, margin, margin)

    layout.add(Image(config.EMAIL_LOGO_URL, width=Decimal(300), height=Decimal(35)))
    layout.add(Paragraph("Refund", font=FONT_BOLD, font_size=FONT_SIZE_TITLE))
    layout.add(_build_refund_info(order, invoice, refund))

    tables = _build_refund_lines(order, refund)
    for num, table in enumerate(tables):
        if num > 0:
            page = Page()
            pdf.add_page(page)
            layout = SingleColumnLayout(page, margin, margin)
        layout.add(table)

    pdf_name_ext = f"Refund number {refund.number}.pdf"
    pdf_path = save_pdf(pdf, pdf_name_ext)
    return pdf_name_ext, pdf_path


def _build_refund_info(
    order: Order, invoice: Invoice, refund: Refund
) -> FixedColumnWidthTable:
    # Left 1 column.
    left_items = []
    if order.billing.company:
        left_items.append(Paragraph(order.billing.company))
    left_items.append(
        Paragraph(f"{order.billing.first_name} {order.billing.last_name}")
    )
    left_items.append(Paragraph(order.billing.address))
    left_items.append(Paragraph(f"{order.billing.zip_code} {order.billing.city}"))
    left_items.append(Paragraph(order.billing.country.name))
    left_items.append(Paragraph(order.billing.email))

    # Middle 1 column.
    middle_items = [
        Paragraph(config.BUSINESS_NAME),
        Paragraph(config.BUSINESS_STREET),
        Paragraph(f"{config.BUSINESS_ZIP_CODE} {config.BUSINESS_CITY}"),
        Paragraph(config.BUSINESS_COUNTRY),
        Paragraph(f"CC: {config.BUSINESS_CC}"),
        Paragraph(f"VAT: {config.BUSINESS_VAT}"),
    ]

    # Right 2 columns.
    right_groups = [
        [
            Paragraph("Order ID", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT),
            Paragraph(f"{order.id}"),
        ],
        [
            Paragraph(
                "Invoice number", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
            ),
            Paragraph(f"{invoice.number}"),
        ],
        [
            Paragraph(
                "Refund number", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
            ),
            Paragraph(f"{refund.number}"),
        ],
        [
            Paragraph(
                "Order date", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
            ),
            Paragraph(order.created_at.strftime("%Y-%m-%d")),
        ],
    ]

    # Create the table.
    row_count = max(len(left_items), len(middle_items), len(right_groups))
    column_widths = [Decimal(4), Decimal(4), Decimal(2), Decimal(2)]
    table = FixedColumnWidthTable(
        number_of_rows=row_count, number_of_columns=4, column_widths=column_widths
    )

    # Append all the rows.
    combined = list(zip_longest(left_items, middle_items, right_groups))
    for l_item, m_item, r_group in combined:
        if l_item is not None:
            table.add(l_item)
        else:
            table.add(Paragraph(" "))
        if m_item is not None:
            table.add(m_item)
        else:
            table.add(Paragraph(" "))
        if r_group is not None:
            for r_item in r_group:
                table.add(r_item)
        else:
            table.add(Paragraph(" "))
            table.add(Paragraph(" "))

    # Finish the table.
    table.set_padding_on_all_cells(Decimal(0), Decimal(2), Decimal(2), Decimal(2))
    table.no_borders()
    return table


def _build_refund_lines(order: Order, refund: Refund) -> list[FixedColumnWidthTable]:
    cells = []
    h_texts = ["Description", "Quantity", "Price"]
    h_widths = [Decimal(64), Decimal(10), Decimal(16)]
    h_count = len(h_texts)

    # headers
    for h_text in h_texts:
        h_paragraph = Paragraph(h_text, color=HexColor("ffffff"))
        h_cell = TableCell(h_paragraph, HexColor("646464"))
        cells.append(h_cell)

    # line
    background_color = HexColor("f0f0f0")

    name_text = "Refund"
    name_p = Paragraph(name_text)
    cells.append(TableCell(name_p, background_color))

    quantity_text = "1"
    quantity_p = Paragraph(quantity_text)
    cells.append(TableCell(quantity_p, background_color))

    price_text = f"{num_to_str(refund.total_price, 2)} {order.currency.code}"
    price_p = Paragraph(price_text)
    cells.append(TableCell(price_p, background_color))

    # empty line
    empty_p = Paragraph(" ")
    cells.append(
        TableCell(empty_p, col_span=h_count, background_color=HexColor("ffffff"))
    )

    # subtotal
    subtotal_head_p = Paragraph(
        "Subtotal", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
    )
    subtotal_value_text = (
        f"{num_to_str(refund.subtotal_price, 2)} {order.currency.code}"
    )
    subtotal_value_p = Paragraph(subtotal_value_text)
    cells.append(TableCell(subtotal_head_p, col_span=h_count - 1))
    cells.append(TableCell(subtotal_value_p, col_span=1))

    # VAT
    vat_head_p = Paragraph(
        f"VAT {refund.vat_percentage}%",
        font=FONT_BOLD,
        horizontal_alignment=Alignment.RIGHT,
    )
    vat_value_text = f"{num_to_str(refund.vat_amount, 2)} {order.currency.code}"
    vat_p = Paragraph(vat_value_text)
    cells.append(TableCell(vat_head_p, col_span=h_count - 1))
    cells.append(TableCell(vat_p, col_span=1))

    # total
    total_head_p = Paragraph(
        "Total", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
    )
    total_value_text = f"{num_to_str(refund.total_price_vat, 2)} {order.currency.code}"
    total_value_p = Paragraph(total_value_text)
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
