from webshop.mail.base import render_email, send_email, pdf_to_string


def send_order_received(
    order_id: int,
    billing_email: str,
    shipping_email: str,
) -> None:
    to = [billing_email, shipping_email]
    subject = f"Costronica Order #{order_id}"
    title = f"Order #{order_id}"
    paragraphs = [
        f"Thank you for your order at Costronica.",
        f"Once your payment is fully processed, you will receive the invoice.",
    ]

    html = render_email(title=title, paragraphs=paragraphs)
    send_email(to, subject, html)


def send_order_paid(
    order_id: int,
    billing_email: str,
    invoice_id: int,
    pdf_path: str,
) -> None:
    to = [billing_email]
    subject = f"Costronica Order #{order_id}"
    title = f"Order #{order_id}"
    paragraphs = [
        f"We have succesfully processed your payment.",
        f"Please see the attachment for your order details.",
    ]
    html = render_email(title=title, paragraphs=paragraphs)
    pdf_str = pdf_to_string(pdf_path)
    pdf_name = f"Invoice #{invoice_id}.pdf"
    pdf_type = "application/docs"
    send_email(to, subject, html, pdf_str, pdf_name, pdf_type)


def send_order_shipped(
    order_id: int,
    billing_email: str,
    shipping_email: str,
    shipping_address: str,
) -> None:
    to = [billing_email, shipping_email]
    subject = f"Costronica Order #{order_id}"
    title = f"Order #{order_id}"
    paragraphs = [
        f"We have handed the order to our carrier.",
        f"Your order will be delivered to {shipping_address}.",
    ]

    html = render_email(title=title, paragraphs=paragraphs)
    send_email(to, subject, html)


def send_order_refund(
    order_id: int,
    billing_email: str,
    refund_id: int,
    pdf_path: str,
) -> None:
    to = [billing_email]
    subject = f"Costronica Order #{order_id}"
    title = f"Order #{order_id}"
    paragraphs = [
        f"We have created a refund for your order.",
        f"Please see the attachment for your refund details.",
    ]

    pdf_str = pdf_to_string(pdf_path)
    pdf_name = f"Refund #{refund_id}.pdf"
    pdf_type = "application/docs"

    html = render_email(title=title, paragraphs=paragraphs)
    send_email(to, subject, html, pdf_str, pdf_name, pdf_type)
