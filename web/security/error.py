class AuthError(Exception):
    pass


class NoValueError(AuthError):
    pass


class KEYError(AuthError):
    pass


class JWTError(AuthError):
    pass


class CSRFError(AuthError):
    pass


class Forbidden(AuthError):
    pass
