import os
from decimal import Decimal

from doc.pdf import Document
from doc.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from doc.pdf.canvas.layout.table.table import TableCell
from doc.pdf.pdf import PDF

DIR = os.path.dirname(os.path.realpath(__file__))


def num_to_str(number: float, decimals: int) -> str:
    return f"{number:.{decimals}f}"


def save_pdf(pdf: Document, pdf_name: str) -> str:
    # Create tmp dir
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    pdf_dir = os.path.join(curr_dir, "tmp")
    if not os.path.isdir(pdf_dir):
        os.makedirs(pdf_dir)
    # Export PDF
    pdf_path = os.path.join(pdf_dir, pdf_name)
    with open(pdf_path, "wb") as file_:
        PDF.dumps(file_, pdf)
    # Return path
    return pdf_path


def cells_to_tables(
    cells: list[TableCell],
    column_count: int,
    column_widths: list[Decimal],
    first_row_count: int,
    other_row_count: int,
    first_top_margin: Decimal,
    other_top_margin: Decimal,
) -> list[FixedColumnWidthTable]:
    cell_lines = []
    cell_line_span = 0
    cell_line = []
    for cell in cells:
        cell_line_span += cell._col_span
        cell_line.append(cell)
        if cell_line_span % column_count == 0:
            cell_lines.append(cell_line)
            cell_line = []

    cell_groups = []
    cell_group_count = 0
    cell_group_split = first_row_count
    cell_group = []
    for cell_line_num, cell_line in enumerate(cell_lines):
        cell_group_count += 1
        cell_group.append(cell_line)
        if cell_group_count % cell_group_split == 0:
            cell_groups.append(cell_group)
            cell_group = []
            cell_group_count = 0
            cell_group_split = other_row_count
        elif cell_line_num == len(cell_lines) - 1:
            cell_groups.append(cell_group)

    tables = []
    for cell_group_num, cell_group in enumerate(cell_groups):
        if cell_group_num == 0:
            margin_top = first_top_margin
        else:
            margin_top = other_top_margin
        table = FixedColumnWidthTable(
            number_of_rows=len(cell_group),
            number_of_columns=column_count,
            margin_top=margin_top,
            column_widths=column_widths,
        )
        for cell_line in cell_group:
            for cell in cell_line:
                table.add(cell)
        table.no_borders()
        tables.append(table)

    return tables
