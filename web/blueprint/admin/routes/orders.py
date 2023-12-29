import csv
import os

from flask import Response, current_app, render_template, request, send_file
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager, joinedload

from web.blueprint.admin import admin_bp
from web.database.client import conn
from web.database.model import (
    Billing,
    Order,
    OrderLine,
    Refund,
    Shipment,
    Shipping,
    Sku,
    SkuDetail,
)
from web.document.objects.invoice import gen_invoice
from web.document.objects.refund import gen_refund
from web.helper.fso import remove_file
from web.helper.pages import render_pages


@admin_bp.get("/admin")
@admin_bp.get("/admin/orders")
def orders() -> str:
    limit = request.args.get("l", type=int, default=40)
    page = request.args.get("p", type=int, default=1)
    offset = (limit * page) - limit
    status_id = request.args.get("status", type=int, default=None)
    search = request.args.get("s", type=str, default=None)

    filters = []
    if status_id is not None:
        filters.append(Order.status_id == status_id)
    if search is not None:
        filters.append(
            or_(
                Shipment.url.ilike(f"%{search}%"),
                Billing.full_name.ilike(f"%{search}%"),
            )
        )

    with conn.begin() as s:
        orders_len = (
            s.query(Order)
            .join(Order.billing)
            .join(Order.shipments, isouter=True)
            .options(
                contains_eager(Order.billing),
                contains_eager(Order.shipments),
            )
            .filter(*filters)
            .count()
        )
        orders_ = (
            s.query(Order)
            .join(Order.billing)
            .join(Order.status)
            .join(Order.currency)
            .join(Order.refunds, isouter=True)
            .join(Order.shipments, isouter=True)
            .options(
                contains_eager(Order.currency),
                contains_eager(Order.status),
                contains_eager(Order.refunds),
                contains_eager(Order.billing),
                contains_eager(Order.shipments),
            )
            .filter(*filters)
            .order_by(Order.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    pages = render_pages(offset, limit, orders_len)
    return render_template(
        "admin/orders.html",
        search=search,
        status_id=status_id,
        orders=orders_,
        pages=pages,
    )


@admin_bp.get("/admin/orders/<int:order_id>")
def order(order_id: int) -> str:
    with conn.begin() as s:
        order_ = (
            s.query(Order)
            .options(
                joinedload(Order.billing),
                joinedload(Order.billing, Billing.country),
                joinedload(Order.currency),
                joinedload(Order.invoice),
                joinedload(Order.lines),
                joinedload(Order.refunds),
                joinedload(Order.shipments),
                joinedload(Order.shipping),
                joinedload(Order.shipping, Shipping.country),
                joinedload(Order.status),
            )
            .filter_by(id=order_id)
            .first()
        )
        order_lines = (
            s.query(OrderLine)
            .options(
                joinedload(OrderLine.sku),
                joinedload(OrderLine.sku, Sku.product),
                joinedload(OrderLine.sku, Sku.details),
                joinedload(OrderLine.sku, Sku.details, SkuDetail.option),
                joinedload(OrderLine.sku, Sku.details, SkuDetail.value),
            )
            .filter_by(order_id=order_id)
            .order_by(OrderLine.id)
            .all()
        )
        refunds = s.query(Refund).filter_by(order_id=order_id).order_by(Refund.id).all()

    return render_template(
        "admin/order.html",
        order=order_,
        order_lines=order_lines,
        refunds=refunds,
    )


@admin_bp.get("/admin/orders/<int:order_id>/invoices/<int:invoice_id>/download")
def download_invoice(order_id: int, invoice_id: int) -> Response:
    with conn.begin() as s:
        order_ = s.query(Order).filter_by(id=order_id).first()
        invoice = order_.invoice
        pdf_name, pdf_path = gen_invoice(s, order_, invoice)
    remove_file(pdf_path, delay_s=20)
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=pdf_name,
    )


@admin_bp.get("/admin/orders/<int:order_id>/refunds/<int:refund_id>/download")
def download_refund(order_id: int, refund_id: int) -> Response:
    with conn.begin() as s:
        order_ = s.query(Order).filter_by(id=order_id).first()
        invoice = order_.invoice
        refund = s.query(Refund).filter_by(id=refund_id).first()
        pdf_name, pdf_path = gen_refund(s, order_, invoice, refund)
    remove_file(pdf_path, delay_s=20)
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=pdf_name,
    )


@admin_bp.get("/admin/orders/<int:order_id>/export")
def download_csv(order_id: int) -> Response:
    with conn.begin() as s:
        order_ = (
            s.query(Order)
            .options(
                joinedload(Order.lines),
                joinedload(Order.lines, OrderLine.sku),
                joinedload(Order.lines, OrderLine.sku, Sku.product),
                joinedload(Order.billing),
                joinedload(Order.billing, Billing.country),
                joinedload(Order.shipping),
                joinedload(Order.shipping, Shipping.country),
            )
            .filter_by(id=order_id)
            .first()
        )

    headers = [
        "Name",
        "Address",
        "ZIP code",
        "City",
        "Country",
        "Phone",
        "Email",
        "SKU",
    ]

    temp_dir = os.path.join(current_app.static_folder, "tmp")
    csv_name = f"Order ID {order_id}.csv"
    csv_path = os.path.join(temp_dir, csv_name)

    with open(csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        order_name = f"{order_.shipping.first_name} {order_.shipping.last_name}"
        order_products = [f"{x.sku.product.name} ({x.sku.id})" for x in order_.lines]
        order_products = ", ".join(order_products)
        writer.writerow(
            [
                order_name,
                order_.shipping.address,
                order_.shipping.zip_code,
                order_.shipping.city,
                order_.shipping.country.name,
                order_.shipping.phone,
                order_.shipping.email,
                order_products,
            ]
        )

    return send_file(
        csv_path,
        as_attachment=True,
        download_name=csv_name,
    )
