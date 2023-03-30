from flask import Blueprint, Response

from webshop.helper.errors import handle_backend_exception

api_v1_bp = Blueprint(
    name="api_v1",
    import_name=__name__,
    url_prefix="/api/v1",
)


@api_v1_bp.errorhandler(Exception)
@handle_backend_exception
def error_handler() -> Response:
    pass
