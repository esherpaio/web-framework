from flask import Blueprint

from web.helper.errors import handle_backend_error

api_v1_bp = Blueprint(
    name="api_v1",
    import_name=__name__,
    url_prefix="/api/v1",
)


@api_v1_bp.errorhandler(Exception)
@handle_backend_error
def error_handler() -> None:
    pass
