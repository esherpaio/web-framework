import itertools
import re
from enum import StrEnum
from typing import Generator

from flask import current_app, has_request_context, request
from markupsafe import Markup

from web.app.urls import url_for
from web.cache import cache
from web.database.model import AppRoute
from web.locale import LocaleStyle, current_locale, expects_locale, gen_locale
from web.setup import config


class MetaTag(StrEnum):
    LINK_ALTERNATE = "<link rel='alternate' hreflang='%s' href='%s'/>"
    LINK_APPLE_TOUCH_ICON = "<link rel='apple-touch-icon' href='%s'/>"
    LINK_CANONICAL = "<link rel='canonical' href='%s'/>"
    LINK_DESCRIBED_BY = "<link rel='describedby' href='%s'/>"
    LINK_ICON = "<link rel='icon' href='%s'/>"
    META_CHARSET = "<meta charset='utf-8'/>"
    META_DESCRIPTION = "<meta name='description' content='%s'/>"
    META_ROBOTS = "<meta name='robots' content='%s'/>"
    META_THEME_COLOR = "<meta name='theme-color' content='%s'/>"
    META_VIEWPORT = "<meta name='viewport' content='width=device-width, initial-scale=1'/>"  # fmt: skip
    OG_DESCRIPTION = "<meta property='og:description' content='%s'/>"
    OG_IMAGE = "<meta property='og:image' content='%s'/>"
    OG_LOCALE = "<meta property='og:locale' content='%s'/>"
    OG_PUBLISHER = "<meta property='article:publisher' content='%s'/>"
    OG_SITE_NAME = "<meta property='og:site_name' content='%s'/>"
    OG_TITLE = "<meta property='og:title' content='%s'/>"
    OG_TYPE = "<meta property='og:type' content='%s'/>"
    OG_URL = "<meta property='og:url' content='%s'/>"
    TITLE = "<title>%s</title>"
    TWITTER_CARD = "<meta name='twitter:card' content='summary_large_image'/>"
    TWITTER_CREATOR = "<meta name='twitter:creator' content='%s'/>"
    TWITTER_IMAGE = "<meta name='twitter:image' content='%s'/>"
    TWITTER_SITE = "<meta name='twitter:site' content='%s'/>"


class RobotTag(StrEnum):
    INDEX_FOLLOW = "index,follow"
    NOINDEX_FOLLOW = "noindex,follow"
    INDEX_NOFOLLOW = "index,nofollow"
    NOINDEX_NOFOLLOW = "noindex,nofollow"
    INDEX_FOLLOW_MAX = "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"  # fmt: skip


class Meta:
    """A class to generate meta tags."""

    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        robots: str | None = None,
        image_url: str | None = None,
        type_: str | None = None,
    ) -> None:
        self._title = title
        self._description = description
        self._robots = robots
        self._image_url = image_url
        self._type = type_ or "website"

    # Properties

    @property
    def title(self) -> str:
        if self._title:
            return self._title
        return config.META_WEBSITE_NAME

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def image_url(self) -> str:
        if self._image_url:
            return self._image_url
        return config.META_LOGO_URL

    @property
    def favicon_url(self) -> str:
        return config.META_FAVICON_URL

    @property
    def logo_url(self) -> str:
        return config.META_LOGO_URL

    @property
    def hex_color(self) -> str:
        return config.META_COLOR_HEX

    @property
    def robots(self) -> str:
        if isinstance(self._robots, str):
            return self._robots
        return "noindex,follow"

    @robots.setter
    def robots(self, robots: str | None) -> None:
        self._robots = robots

    @property
    def canonical_url(self) -> str | None:
        if has_request_context():
            return request.base_url
        return None

    @property
    def llms_url(self) -> str | None:
        if not has_request_context():
            return None
        if "index.llms" not in current_app.view_functions:
            return None
        return url_for("index.llms", _external=True)

    @property
    def alternate_urls(self) -> list[tuple[str, str]]:
        if not has_request_context() or request.endpoint is None:
            return []
        if not expects_locale(request.endpoint):
            return []
        country_codes = sorted(x.code for x in cache.countries if x.in_sitemap)
        language_codes = sorted(x.code for x in cache.languages if x.in_sitemap)
        view_args = request.view_args or {}
        alternates = []
        for country_code, language_code in itertools.product(
            country_codes, language_codes
        ):
            values = view_args | {"_locale": gen_locale(language_code, country_code)}
            alternates.append(
                (
                    gen_locale(language_code, country_code, style=LocaleStyle.BCP47),
                    url_for(request.endpoint, **values, _external=True),
                )
            )
        values = view_args | {"_locale": gen_locale()}
        alternates.append(
            ("x-default", url_for(request.endpoint, **values, _external=True))
        )
        if len({href for _, href in alternates}) < 2:
            return []
        return alternates

    @property
    def locale(self) -> str | None:
        if (
            config.OG_LOCALE
            and current_locale.language_code
            and current_locale.country_code
        ):
            return f"{current_locale.language_code}_{current_locale.country_code}"
        return None

    @property
    def website_name(self) -> str:
        return config.META_WEBSITE_NAME

    @property
    def facebook_url(self) -> str | None:
        return config.SOCIAL_FACEBOOK

    @property
    def twitter_at(self) -> str | None:
        if config.SOCIAL_TWITTER:
            match = re.match(r"^.*twitter\.com/(.*)$", config.SOCIAL_TWITTER)
            if match:
                return f"@{match.group(1)}"
        return None

    # Tags

    @property
    def tags(self) -> Generator[str, None, None]:
        # Meta
        yield Markup(MetaTag.META_CHARSET)
        yield Markup(MetaTag.META_VIEWPORT)
        if self.robots:
            yield Markup(MetaTag.META_ROBOTS % self.robots)
        if self.description:
            yield Markup(MetaTag.META_DESCRIPTION % self.description)
        if self.hex_color:
            yield Markup(MetaTag.META_THEME_COLOR % self.hex_color)
        # Title
        if self.title:
            yield Markup(MetaTag.TITLE % self.title)
        # Link
        if self.canonical_url:
            yield Markup(MetaTag.LINK_CANONICAL % self.canonical_url)
        for hreflang, href in self.alternate_urls:
            yield Markup(MetaTag.LINK_ALTERNATE % (hreflang, href))
        if self.llms_url:
            yield Markup(MetaTag.LINK_DESCRIBED_BY % self.llms_url)
        if self.favicon_url:
            yield Markup(MetaTag.LINK_ICON % self.favicon_url)
        if self.logo_url:
            yield Markup(MetaTag.LINK_APPLE_TOUCH_ICON % self.logo_url)
        # Opengraph
        if self.canonical_url:
            yield Markup(MetaTag.OG_URL % self.canonical_url)
        yield Markup(MetaTag.OG_TYPE % self._type)
        if self.locale:
            yield Markup(MetaTag.OG_LOCALE % self.locale)
        if self.title:
            yield Markup(MetaTag.OG_TITLE % self.title)
        if self.description:
            yield Markup(MetaTag.OG_DESCRIPTION % self.description)
        if self.image_url:
            yield Markup(MetaTag.OG_IMAGE % self.image_url)
        if self.website_name:
            yield Markup(MetaTag.OG_SITE_NAME % self.website_name)
        if self.facebook_url:
            yield Markup(MetaTag.OG_PUBLISHER % self.facebook_url)
        # Twitter
        yield Markup(MetaTag.TWITTER_CARD)
        if self.image_url:
            yield Markup(MetaTag.TWITTER_IMAGE % self.image_url)
        if self.twitter_at:
            yield Markup(MetaTag.TWITTER_SITE % self.twitter_at)
            yield Markup(MetaTag.TWITTER_CREATOR % self.twitter_at)


def gen_meta(route: AppRoute | None = None) -> Meta:
    if isinstance(route, AppRoute):
        return Meta(route.name, route.description, route.robots, route.image_url)
    return Meta()
