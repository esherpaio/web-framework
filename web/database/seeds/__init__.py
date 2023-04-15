from web import config

if config.WEBSHOP_MODE:
    from .order_status import order_status_seeds
    from .product_link_type import product_link_type_seeds
    from .product_type import product_type_seeds

from .currency import currency_seeds
from .file_type import file_type_seeds
from .user_role import user_role_seeds
