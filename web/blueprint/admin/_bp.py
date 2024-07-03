import os

from flask import Blueprint, redirect, url_for
from werkzeug import Response

from web.auth import secure
from web.config import config
from web.database.model import UserRoleLevel
from web.libs.cache import cache
from web.libs.logger import log
from web.libs.meta import Meta

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
@secure(UserRoleLevel.ADMIN)
def authorize() -> None:
    pass


@admin_bp.context_processor
def context() -> dict:
    meta = Meta(title="Admin", robots="noindex,nofollow")
    return dict(cache=cache, config=config, meta=meta)


@admin_bp.errorhandler(Exception)
def error_handler(error: Exception) -> Response:
    log.error(f"Admin error - error {error}", exc_info=True)
    return redirect(url_for("admin.error"))
