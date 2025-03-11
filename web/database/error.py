from web.error import WebError

#
# Base
#


class DbError(WebError):
    pass


class _DbFieldMixin:
    translation_field_key: str | None = None

    def __init__(self, name: str | None = None) -> None:
        field = self.get_field_translation(name)
        if field is not None:
            self.translation_key = self.translation_field_key
            self.translation_kwargs = {"field": field}

    @staticmethod
    def get_field_translation(name: str | None) -> str | None:
        from web.i18n import translator

        if name is not None:
            return translator.translate_strict(f"FIELD_{name.upper()}")
        return None


#
# Database exceptions
#


class ForeignKeyViolationError(WebError):
    code = 409
    translation_key = "API_HTTP_409"


#
# Validation exceptions
#


class DbTypeError(_DbFieldMixin, DbError):
    """Raised when a type does not match."""

    code = 400
    translation_key = "DB_TYPE_ERROR"
    translation_field_key = "DB_TYPE_FIELD_ERROR"


class DbNullError(_DbFieldMixin, DbError):
    """Raised when a value is null."""

    code = 400
    translation_key = "DB_NULL_ERROR"
    translation_field_key = "DB_NULL_FIELD_ERROR"


class DbMinLengthError(_DbFieldMixin, DbError):
    """String length minimum cannot be validated.."""

    code = 400
    translation_key = "DB_MIN_LENGTH_ERROR"
    translation_field_key = "DB_MIN_LENGTH_FIELD_ERROR"


class DbMaxLengthError(_DbFieldMixin, DbError):
    """String length maximum cannot be validated.."""

    code = 400
    translation_key = "DB_MAX_LENGTH_ERROR"
    translation_field_key = "DB_MAX_LENGTH_FIELD_ERROR"


class DbMinNumberError(_DbFieldMixin, DbError):
    """Number minimum cannot be validated ."""

    code = 400
    translation_key = "DB_MIN_NUMBER_ERROR"
    translation_field_key = "DB_MIN_NUMBER_FIELD_ERROR"


class DbMaxNumberError(_DbFieldMixin, DbError):
    """Number maximum cannot be validated ."""

    code = 400
    translation_key = "DB_MAX_NUMBER_ERROR"
    translation_field_key = "DB_MAX_NUMBER_FIELD_ERROR"


class DbPhoneError(DbError):
    """Phone number cannot be validated."""

    code = 400
    translation_key = "DB_PHONE_ERROR"


class DbEmailError(DbError):
    """Email address cannot be validated."""

    code = 400
    translation_key = "DB_EMAIL_ERROR"
