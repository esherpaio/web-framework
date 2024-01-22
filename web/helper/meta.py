import re
from enum import StrEnum
from typing import Generator

from flask import has_request_context, request
from markupsafe import Markup

from web import config
from web.database.model import FlaskRoute

#
# Enumerators
#


class MetaTag(StrEnum):
    LINK_APPLE_TOUCH_ICON = "<link rel='apple-touch-icon' href='%s'/>"
    LINK_CANONICAL = "<link rel='canonical' href='%s'/>"
    LINK_ICON = "<link rel='icon' href='%s'/>"
    META_CHARSET = "<meta http-equiv='Content-Type' charset='utf-8'/>"
    META_DESCRIPTION = "<meta name='description' content='%s'/>"
    META_ROBOTS = "<meta name='robots' content='%s'/>"
    META_THEME_COLOR = "<meta name='theme-color' content='%s'/>"
    META_VIEWPORT = "<meta name='viewport' content='width=device-width, initial-scale=1'/>"  # noqa: E501
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
    TWITTER_SITE = "<meta name='twitter:site' content='%s'/>"


class RobotTag(StrEnum):
    INDEX_FOLLOW = "index, follow"
    NOINDEX_FOLLOW = "noindex, follow"
    INDEX_NOFOLLOW = "index, nofollow"
    NOINDEX_NOFOLLOW = "noindex, nofollow"
    INDEX_FOLLOW_MAX = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"  # noqa: E501


#
# Classes
#


class Meta:
    """A class to generate meta tags."""

    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        robots: str | None = None,
        image_url: str | None = None,
    ) -> None:
        self._title = title
        self._description = description
        self._robots = robots
        self._image_url = image_url

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
    def image_url(self) -> str:
        if self._image_url:
            return self._image_url
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
        if self.favicon_url:
            yield Markup(MetaTag.LINK_ICON % self.favicon_url)
            yield Markup(MetaTag.LINK_APPLE_TOUCH_ICON % self.favicon_url)
        # Opengraph
        if self.canonical_url:
            yield Markup(MetaTag.OG_URL % self.canonical_url)
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
        if self.twitter_at:
            yield Markup(MetaTag.TWITTER_SITE % self.twitter_at)
            yield Markup(MetaTag.TWITTER_CREATOR % self.twitter_at)


#
# Functions
#


def gen_meta(route: FlaskRoute | None = None) -> Meta:
    if isinstance(route, FlaskRoute):
        return Meta(route.name, route.description, route.robots, route.image_url)
    else:
        return Meta()
