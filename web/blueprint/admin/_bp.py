import os

from flask import Blueprint

from web import config
from web.database.model.user_role import UserRoleLevel
from web.helper.cache import cache
from web.helper.meta import Meta
from web.helper.user import access_control

_dir = os.path.dirname(os.path.abspath(__file__))
admin_bp = Blueprint(
    name="admin",
    import_name=__name__,
    static_folder=os.path.join(_dir, "static"),
    static_url_path="/admin/static",
    template_folder=os.path.join(_dir, "templates"),
    url_prefix=None,
)


@admin_bp.before_request
@access_control(UserRoleLevel.ADMIN)
def authorize() -> None:
    pass


@admin_bp.context_processor
def context() -> dict:
    meta = Meta(title="Admin", robots="noindex,nofollow")
    return dict(cache=cache, config=config, meta=meta)
