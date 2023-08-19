from flask import Blueprint

from web.helper.errors import handle_backend_error

webhook_v1_bp = Blueprint(
    name="webhook_v1",
    import_name=__name__,
    url_prefix="/webhook/v1",
)


@webhook_v1_bp.errorhandler(Exception)
@handle_backend_error
def error_handler() -> None:
    pass
