import os

from flask import Blueprint
from werkzeug import Response

from web.app.javascript import js_bundle
from web.app.meta import Meta
from web.auth import authorize_user
from web.automation.task import StaticJob, StaticType
from web.database.model import AppBlueprint, UserRoleLevel
from web.packer.bundle import CssBundle

_dir = os.path.dirname(os.path.abspath(__file__))
admin_v1_bp = Blueprint(
    name="admin",
    import_name=__name__,
    url_prefix=None,
    template_folder=os.path.join(_dir, "templates"),
    static_folder=os.path.join(_dir, "static"),
    static_url_path="/admin/static",
)
admin_v1_static_jobs = [
    StaticJob(
        type_=StaticType.CSS,
        bundles=[CssBundle(os.path.join(_dir, "static", "admin_v1.css"))],
        model=AppBlueprint,
        endpoint="admin",
    ),
    StaticJob(
        type_=StaticType.JS,
        bundles=[js_bundle],
        model=AppBlueprint,
        endpoint="admin",
    ),
]


@admin_v1_bp.before_request
def authorize() -> Response | None:
    return authorize_user(UserRoleLevel.ADMIN)


@admin_v1_bp.context_processor
def context() -> dict:
    meta = Meta(title="Admin", robots="noindex,nofollow")
    return dict(meta=meta)
