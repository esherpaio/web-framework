from web.helper.exceptions import WebError


class DbError(WebError):
    """Base class for database errors."""

    pass


class DbLengthError(DbError):
    """Raised when a string length cannot be validated.."""

    code = 400


class DbNumberError(DbError):
    """Raised when a number cannot be validated ."""

    code = 400


class DbEmailError(DbError):
    """Raised when an email address cannot be validated."""

    code = 400
    translation_key = "DATABASE_EMAIL_ERROR"


class DbPhoneError(DbError):
    """Raised when a phone number cannot be validated."""

    code = 400
    translation_key = "DATABASE_PHONE_ERROR"
