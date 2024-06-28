from web.libs.errors import WebError

#
# Super
#


class APIError(WebError):
    """Base class for API errors."""

    pass


#
# Sub
#


class APITypeError(APIError):
    """Raised when a type does not match."""

    code = 400


class APINullError(APIError):
    """Raised when a value is null."""

    code = 400
