import os

from web.pdf.pdf import PDF, Document

DIR = os.path.dirname(os.path.realpath(__file__))


def float_to_str(x: float) -> str:
    return f"{x:.2f}"


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
