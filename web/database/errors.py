from web.libs.errors import WebError

#
# Super
#


class DbError(WebError):
    """Base class for database errors."""

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
# Sub
#


class DbPhoneError(DbError):
    """Phone number cannot be validated."""

    code = 400
    translation_key = "DATABASE_PHONE_ERROR"


class DbEmailError(DbError):
    """Email address cannot be validated."""

    code = 400
    translation_key = "DATABASE_EMAIL_ERROR"


class DbLengthMinError(_DbFieldMixin, DbError):
    """String length minimum cannot be validated.."""

    code = 400
    translation_key = "DATABASE_LENGTH_MIN_ERROR"
    translation_field_key = "DATABASE_LENGTH_MIN_FIELD_ERROR"


class DbLengthMaxError(_DbFieldMixin, DbError):
    """String length maximum cannot be validated.."""

    code = 400
    translation_key = "DATABASE_LENGTH_MAX_ERROR"
    translation_field_key = "DATABASE_LENGTH_MAX_FIELD_ERROR"


class DbNumberMinError(_DbFieldMixin, DbError):
    """Number minimum cannot be validated ."""

    code = 400
    translation_key = "DATABASE_NUMBER_MIN_ERROR"
    translation_field_key = "DATABASE_NUMBER_MIN_FIELD_ERROR"


class DbNumberMaxError(_DbFieldMixin, DbError):
    """Number maximum cannot be validated ."""

    code = 400
    translation_key = "DATABASE_NUMBER_MAX_ERROR"
    translation_field_key = "DATABASE_NUMBER_MAX_FIELD_ERROR"
