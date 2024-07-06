import os

from flask import Blueprint

from web.auth import authorize
from web.cache import cache
from web.config import config
from web.database.model import UserRoleLevel
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
@authorize(UserRoleLevel.ADMIN)
def _authorize() -> None:
    pass


@admin_bp.context_processor
def context() -> dict:
    meta = Meta(title="Admin", robots="noindex,nofollow")
    return dict(cache=cache, config=config, meta=meta)
