import re
from enum import StrEnum

from flask import has_request_context, request
from markupsafe import Markup

from web import config
from web.database.model import Page


class MetaLine(StrEnum):
    LINK_APPLE_TOUCH_ICON = "<link rel='apple-touch-icon' href='%s'/>"
    LINK_CANONICAL = "<link rel='canonical' href='%s'/>"
    LINK_ICON = "<link rel='icon' href='%s'/>"
    META_CHARSET = "<meta http-equiv='Content-Type' charset='utf-8'/>"
    META_DESCRIPTION = "<meta name='description' content='%s'/>"
    META_ROBOTS = "<meta name='robots' content='%s'/>"
    META_THEME_COLOR = "<meta name='theme-color' content='%s'/>"
    META_VIEWPORT = (
        "<meta name='viewport' content='width=device-width, initial-scale=1'/>"
    )
    OG_DESCRIPTION = "<meta property='og:description' content='%s'/>"
    OG_LOCALE = "<meta property='og:locale' content='%s'/>"
    OG_PUBLISHER = "<meta property='article:publisher' content='%s'/>"
    OG_SITE_NAME = "<meta property='og:site_name' content='%s'/>"
    OG_TITLE = "<meta property='og:title' content='%s'/>"
    OG_TYPE = "<meta property='og:type' content='%s'/>"
    OG_URL = "<meta property='og:url' content='%s'/>"
    OG_IMAGE = "<meta property='og:image' content='%s'/>"
    TITLE = "<title>%s</title>"
    TWITTER_CARD = "<meta name='twitter:card' content='summary_large_image'/>"
    TWITTER_CREATOR = "<meta name='twitter:creator' content='%s'/>"
    TWITTER_SITE = "<meta name='twitter:site' content='%s'/>"


class Meta:
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        robots: str | None = None,
        img_url: str | None = None,
    ) -> None:
        self._title = title
        self._description = description
        self._robots = robots
        self._img_url = img_url

    # Properties

    @property
    def title(self) -> str:
        if self._title:
            return f"{self._title} • {config.WEBSITE_NAME}"
        else:
            return config.WEBSITE_NAME

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def img_url(self) -> str:
        if self._img_url:
            return self._img_url
        else:
            return config.WEBSITE_LOGO_URL

    @property
    def favicon_url(self) -> str:
        return config.WEBSITE_FAVICON_URL

    @property
    def hex_color(self) -> str:
        return config.WEBSITE_HEX_COLOR

    @property
    def robots(self) -> str:
        if isinstance(self._robots, str):
            return self._robots
        else:
            return config.ROBOT_DEFAULT_TAGS

    @property
    def canonical_url(self) -> str | None:
        if has_request_context():
            return request.base_url

    @property
    def locale(self) -> str | None:
        if config.WEBSITE_LANGUAGE_CODE and config.WEBSITE_COUNTRY_CODE:
            return f"{config.WEBSITE_LANGUAGE_CODE}_{config.WEBSITE_COUNTRY_CODE}"

    @property
    def website_name(self) -> str:
        return config.WEBSITE_NAME

    @property
    def facebook_url(self) -> str | None:
        return config.SOCIAL_FACEBOOK

    @property
    def twitter_at(self) -> str | None:
        if config.SOCIAL_TWITTER:
            match = re.match(r"^.*twitter\.com/(.*)$", config.SOCIAL_TWITTER)
            if match:
                return f"@{match.group(1)}"

    # Tags

    @property
    def tags(self) -> list[str]:
        # Meta
        yield Markup(MetaLine.META_CHARSET)
        yield Markup(MetaLine.META_VIEWPORT)
        if self.robots:
            yield Markup(MetaLine.META_ROBOTS % self.robots)
        if self.description:
            yield Markup(MetaLine.META_DESCRIPTION % self.description)
        if self.hex_color:
            yield Markup(MetaLine.META_THEME_COLOR % self.hex_color)
        # Title
        if self.title:
            yield Markup(MetaLine.TITLE % self.title)
        # Links
        if self.canonical_url:
            yield Markup(MetaLine.LINK_CANONICAL % self.canonical_url)
        if self.favicon_url:
            yield Markup(MetaLine.LINK_ICON % self.favicon_url)
            yield Markup(MetaLine.LINK_APPLE_TOUCH_ICON % self.favicon_url)
        # Opengraph
        if self.canonical_url:
            yield Markup(MetaLine.OG_URL % self.canonical_url)
        if self.locale:
            yield Markup(MetaLine.OG_LOCALE % self.locale)
        if self.title:
            yield Markup(MetaLine.OG_TITLE % self.title)
        if self.description:
            yield Markup(MetaLine.OG_DESCRIPTION % self.description)
        if self.img_url:
            yield Markup(MetaLine.OG_IMAGE % self.img_url)
        if self.website_name:
            yield Markup(MetaLine.OG_SITE_NAME % self.website_name)
        if self.facebook_url:
            yield Markup(MetaLine.OG_PUBLISHER % self.facebook_url)
        # Twitter
        yield Markup(MetaLine.TWITTER_CARD)
        if self.twitter_at:
            yield Markup(MetaLine.TWITTER_SITE % self.twitter_at)
            yield Markup(MetaLine.TWITTER_CREATOR % self.twitter_at)


def gen_meta(page: Page = None) -> Meta:
    if isinstance(page, Page):
        return Meta(page.name, page.desc, page.robots)
    else:
        return Meta()
