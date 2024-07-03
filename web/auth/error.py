from web.api.utils import ApiText


class AuthError(Exception):
    code = 401
    message = ApiText.HTTP_401


class NoValueError(AuthError):
    pass


class KEYError(AuthError):
    pass


class JWTError(AuthError):
    pass


class CSRFError(AuthError):
    pass


class Forbidden(AuthError):
    code = 403
    message = ApiText.HTTP_403
