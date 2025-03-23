from web.api import HttpText


class AuthError(Exception):
    name = ""
    code = 401
    message = HttpText.HTTP_401


class NoValueError(AuthError):
    name = "NoValueError: missing value"


class KEYError(AuthError):
    name = "KEYError: Key authentication failed"


class JWTError(AuthError):
    name = "JWTError: JWT authentication failed"


class CSRFError(AuthError):
    name = "CSRFError: CSRF verification failed"


class Forbidden(AuthError):
    name = "Forbidden: authorization failed"
    code = 403
    message = HttpText.HTTP_403
