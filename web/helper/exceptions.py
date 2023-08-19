#
# Classes
#


class WebError(Exception):
    """Base class for web errors."""

    code: int = 400
    translation_key: str | None = None
