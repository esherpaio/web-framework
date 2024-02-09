from flask import Blueprint

from web.libs.app import handle_backend_error

api_v1_bp = Blueprint(
    name="api_v1",
    import_name=__name__,
    url_prefix="/api/v1",
)
api_v1_bp.register_error_handler(Exception, handle_backend_error)
