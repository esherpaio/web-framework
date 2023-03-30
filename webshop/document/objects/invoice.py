from decimal import Decimal
from itertools import zip_longest

from borb.pdf import Document, Image
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.page.page import Page

from webshop import config
from webshop.database.model import Order, Invoice
from webshop.document._base import FONT_BOLD, FONT_SIZE_TITLE, Paragraph, TableCell
from webshop.document._utils import save_pdf, num_to_string, cells_to_tables


def gen_invoice(order: Order, invoice: Invoice) -> tuple[str, str]:
    pdf = Document()
    page = Page()
    pdf.add_page(page)
    margin = Decimal(30)
    layout = SingleColumnLayout(page, margin, margin)

    layout.add(Image(config.EMAIL_LOGO, width=Decimal(300), height=Decimal(35)))
    layout.add(Paragraph("Invoice", font=FONT_BOLD, font_size=FONT_SIZE_TITLE))
    layout.add(_build_order_info(order, invoice))

    tables = _build_order_lines(order)
    for num, table in enumerate(tables):
        if num > 0:
            page = Page()
            pdf.add_page(page)
            layout = SingleColumnLayout(page, margin, margin)
        layout.add(table)

    pdf_name_ext = f"Invoice number {invoice.number}.pdf"
    pdf_path = save_pdf(pdf, pdf_name_ext)
    return pdf_name_ext, pdf_path


def _build_order_info(order: Order, invoice: Invoice) -> FixedColumnWidthTable:
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
    for le, mi, ri in combined:
        if le is not None:
            table.add(le)
        else:
            table.add(Paragraph(" "))
        if mi is not None:
            table.add(mi)
        else:
            table.add(Paragraph(" "))
        if ri is not None:
            for r_item in ri:
                table.add(r_item)
        else:
            table.add(Paragraph(" "))
            table.add(Paragraph(" "))

    # Finish the table.
    table.set_padding_on_all_cells(Decimal(0), Decimal(2), Decimal(2), Decimal(2))
    table.no_borders()
    return table


def _build_order_lines(order: Order) -> list[FixedColumnWidthTable]:
    cells = []
    h_texts = ["Description", "Quantity", "Price"]
    h_widths = [Decimal(64), Decimal(10), Decimal(16)]
    h_count = len(h_texts)

    # headers
    for h_text in h_texts:
        h_paragraph = Paragraph(h_text, color=HexColor("ffffff"))
        h_cell = TableCell(h_paragraph, HexColor("646464"))
        cells.append(h_cell)

    # lines
    for num, order_line in enumerate(order.lines):
        background_color = HexColor("f0f0f0") if num % 2 else HexColor("ffffff")

        name_text = f"{order_line.sku.product.name}"
        name_p = Paragraph(name_text)
        cells.append(TableCell(name_p, background_color))

        quantity_text = f"{order_line.quantity}"
        quantity_p = Paragraph(quantity_text)
        cells.append(TableCell(quantity_p, background_color))

        price_text = f"{num_to_string(order_line.total_price, 2)} {order.currency.code}"
        price_p = Paragraph(price_text)
        cells.append(TableCell(price_p, background_color))

    # empty line
    empty_p = Paragraph(" ")
    cells.append(
        TableCell(empty_p, col_span=h_count, background_color=HexColor("ffffff"))
    )

    # subtotal
    subtotal_head_p = Paragraph(
        "Items", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
    )
    subtotal_value_text = (
        f"{num_to_string(order.subtotal_price, 2)} {order.currency.code}"
    )
    subtotal_value_p = Paragraph(subtotal_value_text)
    cells.append(
        TableCell(subtotal_head_p, col_span=h_count - 1, border_color="000000", border_bottom=True)
    )
    cells.append(TableCell(subtotal_value_p, col_span=1, border_color="000000"))

    # discount
    subtotal_head_p = Paragraph(
        "Discount", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
    )
    subtotal_value_text = (
        f"{num_to_string(order.discount_price, 2)} {order.currency.code}"
    )
    subtotal_value_p = Paragraph(subtotal_value_text)
    cells.append(TableCell(subtotal_head_p, col_span=h_count - 1))
    cells.append(TableCell(subtotal_value_p, col_span=1))

    # shipment
    subtotal_head_p = Paragraph(
        "Shipment", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
    )
    subtotal_value_text = (
        f"{num_to_string(order.shipment_price, 2)} {order.currency.code}"
    )
    subtotal_value_p = Paragraph(subtotal_value_text)
    cells.append(TableCell(subtotal_head_p, col_span=h_count - 1))
    cells.append(TableCell(subtotal_value_p, col_span=1))

    # VAT
    vat_head_p = Paragraph(
        f"VAT {order.vat_percentage}%",
        font=FONT_BOLD,
        horizontal_alignment=Alignment.RIGHT,
    )
    vat_value_text = f"{num_to_string(order.vat_amount, 2)} {order.currency.code}"
    vat_p = Paragraph(vat_value_text)
    cells.append(TableCell(vat_head_p, col_span=h_count - 1))
    cells.append(TableCell(vat_p, col_span=1))

    # total
    total_head_p = Paragraph(
        "Total", font=FONT_BOLD, horizontal_alignment=Alignment.RIGHT
    )
    total_value_text = (
        f"{num_to_string(order.total_price_vat, 2)} {order.currency.code}"
    )
    total_value_p = Paragraph(total_value_text)
    cells.append(TableCell(total_head_p, col_span=h_count - 1))
    cells.append(TableCell(total_value_p, col_span=1))

    # empty line
    empty_p = Paragraph(" ")
    cells.append(
        TableCell(empty_p, col_span=h_count, background_color=HexColor("ffffff"))
    )

    # note
    note_1_text = "Please follow the payment instructions from Mollie."
    note_1_p = Paragraph(note_1_text, horizontal_alignment=Alignment.RIGHT)
    cells.append(TableCell(note_1_p, col_span=h_count))

    return cells_to_tables(
        cells,
        h_count,
        h_widths,
        first_row_count=30,
        other_row_count=42,
        first_top_margin=Decimal(24),
        other_top_margin=Decimal(0),
    )
