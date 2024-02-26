from web.libs.errors import WebError


class DbError(WebError):
    """Base class for database errors."""

    pass


class DbLengthError(DbError):
    """String length cannot be validated.."""

    code = 400


class DbNumberError(DbError):
    """Number cannot be validated ."""

    code = 400


class DbEmailError(DbError):
    """Email address cannot be validated."""

    code = 400
    translation_key = "DATABASE_EMAIL_ERROR"


class DbPhoneError(DbError):
    """Phone number cannot be validated."""

    code = 400
    translation_key = "DATABASE_PHONE_ERROR"
