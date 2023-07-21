class DbError(Exception):
    """Base class for database errors."""

    pass


class DbLengthError(DbError):
    """Raised when a string length cannot be validated.."""

    pass


class DbNumberError(DbError):
    """Raised when a number cannot be validated ."""

    pass


class DbRegexError(DbError):
    """Raised when a regex pattern is not matched."""

    pass


class DbEmailError(DbError):
    """Raised when an email address cannot be validated."""

    pass


class DbPhoneError(DbError):
    """Raised when a phone number cannot be validated."""

    pass
