import os

from flask import Blueprint

from web.app.meta import gen_meta
from web.app.routing import get_route
from web.app.schema import gen_schemas
from web.packer.bundle import JsBundle

_dir = os.path.dirname(os.path.abspath(__file__))
auth_v1_bp = Blueprint(
    name="auth",
    import_name=__name__,
    url_prefix=None,
    template_folder=os.path.join(_dir, "templates"),
    static_folder=os.path.join(_dir, "static"),
    static_url_path="/auth/static",
)
auth_v1_js_bundle = JsBundle(os.path.join(_dir, "static", "auth_v1.js"))


@auth_v1_bp.context_processor
def context() -> dict:
    route = get_route()
    meta = gen_meta(route)
    schemas = gen_schemas(route)
    return dict(meta=meta, schemas=schemas)
