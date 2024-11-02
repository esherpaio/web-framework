import os

from flask import Blueprint

_dir = os.path.dirname(os.path.abspath(__file__))
robots_bp = Blueprint(
    name="robots",
    import_name=__name__,
    url_prefix=None,
    template_folder=os.path.join(_dir, "templates"),
    static_folder=os.path.join(_dir, "static"),
    static_url_path="/robots/static",
)
