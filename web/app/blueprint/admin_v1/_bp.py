import os

from flask import Blueprint
from werkzeug import Response

from web.app.meta import Meta
from web.app.static import js_bundle
from web.auth import authorize_user
from web.automation.task import StaticSeed, StaticType
from web.database.model import AppRoute, UserRoleLevel
from web.packer.bundle import CssBundle, JsBundle

_dir = os.path.dirname(os.path.abspath(__file__))
admin_v1_bp = Blueprint(
    name="admin",
    import_name=__name__,
    url_prefix=None,
    template_folder=os.path.join(_dir, "templates"),
    static_folder=os.path.join(_dir, "static"),
    static_url_path="/admin/static",
)
admin_v1_css_bundle = CssBundle(os.path.join(_dir, "static", "admin_v1.css"))
admin_v1_js_bundle = js_bundle
admin_v1_js_seeds = [
    StaticSeed(
        type_=StaticType.JS,
        bundles=[JsBundle(os.path.join(_dir, "static", "orders_add.js"))],
        model=AppRoute,
        endpoint="admin.orders_add",
    ),
]
admin_v1_routes = [
    AppRoute(id=100, endpoint="admin.orders_add"),
]


@admin_v1_bp.before_request
def authorize() -> Response | None:
    return authorize_user(UserRoleLevel.ADMIN)


@admin_v1_bp.context_processor
def context() -> dict:
    meta = Meta(title="Admin", robots="noindex,nofollow")
    return dict(meta=meta)
