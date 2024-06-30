class SecurityError(Exception):
    pass


class JWTError(SecurityError):
    pass


class CSRFError(SecurityError):
    pass


class NoAuthorizationError(SecurityError):
    pass


class Forbidden(SecurityError):
    pass
