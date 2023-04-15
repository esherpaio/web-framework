from webshop import config

if config.WEBSHOP_MODE:
    from .order_status import OrderStatusSyncer
    from .product_link_type import ProductLinkeTypeSyncer
    from .product_type import ProductTypeSyncer
    from .sku import SkuSyncer

from .country import CountrySyncer
from .currency import CurrencySyncer
from .file_type import FileTypeSyncer
from .region import RegionSyncer
from .user_role import UserRoleSyncer
