class WebError(Exception):
    code: int = 400
    translation_key: str | None = None
    translation_kwargs: dict = {}
