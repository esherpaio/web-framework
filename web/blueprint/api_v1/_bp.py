from flask import Blueprint

api_v1_bp = Blueprint(
    name="api_v1",
    import_name=__name__,
    url_prefix="/api/v1",
)
