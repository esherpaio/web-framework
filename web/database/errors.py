class DbError(Exception):
    """Base class for database errors."""

    pass


class DbLengthError(DbError):
    """Raised when the validation length is not met."""

    pass


class DbEmailError(DbError):
    """Raised when an email address cannot be validated."""

    pass


class DbPhoneError(DbError):
    """Raised when a phone number cannot be validated."""

    pass


class DbSlugError(DbError):
    """Raised when a slug cannot be validated."""

    pass
