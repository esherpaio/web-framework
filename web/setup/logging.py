from http import HTTPStatus

import flask.cli
import werkzeug.serving
from werkzeug.serving import WSGIRequestHandler

werkzeug_log = werkzeug.serving._log


class CustomWsgiRequestHandler(WSGIRequestHandler):
    def log_request(self, code: int | str = "NA", *args, **kwargs) -> None:
        if isinstance(code, HTTPStatus):
            code = code.value
        method = getattr(self, "command", "NA")
        path = getattr(self, "path", "")
        werkzeug_log("info", f"{method} {code} {path}")


def quiet_werkzeug_log(type, message, *args, **kwargs):
    ignore = ["press ctrl+c to quit", "running on"]
    if any(ig in message.lower() for ig in ignore):
        return
    werkzeug_log(type, message, *args, **kwargs)


def patch_logging() -> None:
    # Ignore startup messages from Werkzeug
    werkzeug.serving._log = quiet_werkzeug_log
    # Shorten request logging format
    werkzeug.serving.WSGIRequestHandler = CustomWsgiRequestHandler  # type: ignore[misc]
    # Ignore startup messages from Flask
    flask.cli.show_server_banner = lambda *args, **kwargs: None
