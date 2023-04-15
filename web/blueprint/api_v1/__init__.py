from web import config
from ._bp import api_v1_bp

if config.WEBSHOP_MODE:
    from .routes import (
        cart,
        cart_item,
        coupon,
        order,
        order_payment,
        order_refund,
        order_shipment,
        product,
        product_link,
        product_media,
        product_option,
        product_value,
        shipment_class,
        shipment_method,
        shipment_zone,
        sku,
    )

from .routes import (
    article,
    article_media,
    billing,
    category,
    category_item,
    email,
    session,
    shipping,
    user,
)
