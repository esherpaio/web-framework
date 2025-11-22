import flask.cli
import werkzeug.serving
from werkzeug.serving import WSGIRequestHandler

from web.logger import AnsiColor

werkzeug_log = werkzeug.serving._log


class CustomWsgiRequestHandler(WSGIRequestHandler):
    def log_request(self, code: int | str = "NA", *args, **kwargs) -> None:
        code = str(code)
        method = getattr(self, "command", "NA")
        path = getattr(self, "path", "")
        message = f"{method} {code} {path}"

        match code[0]:
            case "2":
                color_int = AnsiColor.DEBUG.value
                message = f"\x1b[{color_int}m{message}\x1b[0m"
            case "3":
                color_int = AnsiColor.WARNING.value
                message = f"\x1b[{color_int}m{message}\x1b[0m"
            case "4" | "5":
                color_int = AnsiColor.ERROR.value
                message = f"\x1b[{color_int}m{message}\x1b[0m"

        werkzeug_log("info", message)


def quiet_werkzeug_log(type, message, *args, **kwargs) -> None:
    lines = message.split("\n")
    if (
        len(lines) > 1
        and lines[1].startswith(" * ")
        and "running on http" in lines[1].lower()
    ):
        message = lines[1].removeprefix(" * ")
    werkzeug_log(type, message, *args, **kwargs)


def patch_logging() -> None:
    # Ignore startup messages from Werkzeug
    werkzeug.serving._log = quiet_werkzeug_log
    # Shorten request logging format
    werkzeug.serving.WSGIRequestHandler = CustomWsgiRequestHandler  # type: ignore[misc]
    # Ignore startup messages from Flask
    flask.cli.show_server_banner = lambda *args, **kwargs: None
