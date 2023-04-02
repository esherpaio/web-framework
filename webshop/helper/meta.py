from flask import request

from webshop import config
from webshop.database.model import Page


class Meta:
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        robots: str | None = None,
    ) -> None:
        self._title = title
        self._description = description
        self._robots = robots

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
    def canonical_url(self) -> str:
        return request.base_url


def gen_meta(page: Page = None) -> Meta:
    if isinstance(page, Page):
        return Meta(page.name, page.desc, page.robots)
    else:
        return Meta()
