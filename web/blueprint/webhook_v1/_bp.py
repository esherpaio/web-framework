from flask import Blueprint

from web.libs.app import handle_backend_error

webhook_v1_bp = Blueprint(
    name="webhook_v1",
    import_name=__name__,
    url_prefix="/webhook/v1",
)
webhook_v1_bp.register_error_handler(Exception, handle_backend_error)
