class WebError(Exception):
    code: int = 400
    translation_key: str | None = None
    translation_kwargs: dict = {}


class ConfigError(WebError):
    code = 500

    def __init__(self, config_key: str) -> None:
        self.config_key = config_key
        message = f"Config error: {config_key} is not set or invalid"
        super().__init__(message)

    def __str__(self) -> str:
        return f"ConfigError ({self.config_key})"
