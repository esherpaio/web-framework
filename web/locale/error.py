from web.error import WebError


class CountryNotFoundError(WebError):
    pass


class CurrencyNotFoundError(WebError):
    pass


class LanguageNotFoundError(WebError):
    pass
