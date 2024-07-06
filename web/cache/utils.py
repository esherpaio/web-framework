from web.database import conn
from web.database.model import (
    AppBlueprint,
    AppRoute,
    AppSetting,
    Country,
    Currency,
    FileType,
    Language,
    OrderStatus,
    ProductLinkType,
    ProductType,
    Redirect,
    Region,
    UserRole,
)

from .cache import cache


def cache_common() -> None:
    with conn.begin() as s:
        # fmt: off
        cache.blueprints = s.query(AppBlueprint).all()
        cache.countries = s.query(Country).order_by(Country.name).all()
        cache.currencies = s.query(Currency).order_by(Currency.code).all()
        cache.file_types = s.query(FileType).order_by(FileType.name).all()
        cache.languages = s.query(Language).order_by(Language.code).all()
        cache.order_statuses = s.query(OrderStatus).order_by(OrderStatus.order).all()
        cache.product_link_types = s.query(ProductLinkType).order_by(ProductLinkType.name).all()
        cache.product_types = s.query(ProductType).order_by(ProductType.name).all()
        cache.redirects = s.query(Redirect).order_by(Redirect.url_from.desc()).all()
        cache.regions = s.query(Region).order_by(Region.name).all()
        cache.routes = s.query(AppRoute).all()
        cache.setting = s.query(AppSetting).first()
        cache.user_roles = s.query(UserRole).order_by(UserRole.name).all()
        # fmt: on
