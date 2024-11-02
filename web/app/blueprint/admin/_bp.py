import os

from flask import Blueprint
from werkzeug import Response

from web.app.meta import Meta
from web.auth import authorize_user
from web.database.model import UserRoleLevel

_dir = os.path.dirname(os.path.abspath(__file__))
admin_bp = Blueprint(
    name="admin",
    import_name=__name__,
    url_prefix=None,
    template_folder=os.path.join(_dir, "templates"),
    static_folder=os.path.join(_dir, "static"),
    static_url_path="/admin/static",
)


@admin_bp.before_request
def authorize() -> Response | None:
    return authorize_user(UserRoleLevel.ADMIN)


@admin_bp.context_processor
def context() -> dict:
    meta = Meta(title="Admin", robots="noindex,nofollow")
    return dict(meta=meta)
