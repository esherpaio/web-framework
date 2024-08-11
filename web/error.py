class WebError(Exception):
    """Base class for errors."""

    code: int = 400
    translation_key: str | None = None
    translation_kwargs: dict = {}
