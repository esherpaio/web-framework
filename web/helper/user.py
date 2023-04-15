from enum import StrEnum
from functools import cached_property

from flask import request, session
from flask_login import AnonymousUserMixin
from sqlalchemy.orm import joinedload

from web import config
from web.database.client import conn
from web.database.model import Country, Currency, Language, User
from web.helper.cache import cache
from web.helper.locale import cur_locale, match_locale


class Header(StrEnum):
    COUNTRY = "cf-ipcountry"


class Session(StrEnum):
    CART_COUNT = "cart_count"
    KEY = "key"
    LOCALE = "locale"
    REDIRECT = "redirect"


class UserAttrs:
    @cached_property
    def locale(self) -> str:
        view_locale = cur_locale()
        session_locale = session.get(Session.LOCALE)
        locale = view_locale or session_locale or config.WEBSITE_LOCALE
        session[Session.LOCALE] = locale
        return locale

    @cached_property
    def locale_info(self) -> tuple[str, str]:
        language, country = match_locale(self.locale)

        if not country:
            header_country = request.headers.get(Header.COUNTRY)
            country = header_country or config.BUSINESS_COUNTRY_CODE
        if not language:
            language = config.WEBSITE_LANGUAGE_CODE

        country = country.upper()
        language = language.lower()
        return country, language

    @cached_property
    def country(self) -> Country:
        country_code, _ = self.locale_info
        for country in cache.countries:
            if country.code == country_code:
                return country

    @cached_property
    def currency(self) -> Currency:
        currency_id = self.country.currency_id
        for currency in cache.currencies:
            if currency.id == currency_id:
                return currency

    @cached_property
    def language(self) -> Language:
        _, language_code = self.locale_info
        for language in cache.languages:
            if language.code == language_code:
                return language

    @property
    def cart_count(self) -> int:
        return session.get(Session.CART_COUNT, 0)

    @cart_count.setter
    def cart_count(self, value: int) -> None:
        session[Session.CART_COUNT] = value

    @property
    def redirect(self) -> str | None:
        return session.get(Session.REDIRECT)

    @redirect.setter
    def redirect(self, value: str | None) -> None:
        session[Session.REDIRECT] = value

    @property
    def key(self) -> str | None:
        return session.get(Session.KEY)

    @key.setter
    def key(self, value: str | None) -> None:
        session[Session.KEY] = value


class KnownUser(User, UserAttrs):
    def __init__(self, user: User) -> None:
        super().__init__()

        for key, value in vars(user).items():
            if key.startswith("_"):
                continue
            setattr(self, key, value)

        if not hasattr(self, "is_active"):
            self.is_active = False

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> int:
        return self.id


class GuestUser(AnonymousUserMixin, UserAttrs):
    pass


def load_user(user_id: int) -> KnownUser | None:
    with conn.begin() as s:
        user = (
            s.query(User)
            .options(joinedload(User.role))
            .filter_by(id=user_id, is_active=True)
            .first()
        )
    if user is not None:
        return KnownUser(user)
