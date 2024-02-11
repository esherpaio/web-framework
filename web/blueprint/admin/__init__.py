from ._bp import admin_bp
from .routes import (
    categories,
    countries,
    coupons,
    error,
    orders,
    products,
    setting,
    shipment_classes,
    shipment_methods,
    shipment_zones,
    users,
)

__all__ = [
    "admin_bp",
    "categories",
    "countries",
    "coupons",
    "error",
    "orders",
    "products",
    "setting",
    "shipment_classes",
    "shipment_methods",
    "shipment_zones",
    "users",
]
