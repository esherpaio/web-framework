import os
from decimal import ROUND_HALF_UP, Decimal

DIR = os.path.dirname(os.path.realpath(__file__))


def format_decimal(value: Decimal) -> str:
    quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return str(quantized)


def get_pdf_path(pdf_name: str) -> str:
    if not pdf_name.endswith(".pdf"):
        pdf_name = f"{pdf_name}.pdf"
    pdf_dir = os.path.join(DIR, "tmp")
    if not os.path.isdir(pdf_dir):
        os.makedirs(pdf_dir)
    pdf_path = os.path.join(pdf_dir, pdf_name)
    return pdf_path
