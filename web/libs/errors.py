#
# Base
#


class WebError(Exception):
    """Base class for errors."""

    code: int = 400
    translation_key: str | None = None


#
# API
#


class APIError(WebError):
    """Base class for API errors."""

    pass


class APITypeError(APIError):
    """Raised when a type does not match."""

    code = 400


class APINullError(APIError):
    """Raised when a value is null."""

    code = 400
