from web.app.urls import url_for


class Sitemap:
    def __init__(self, endpoint: str) -> None:
        self._endpoint = endpoint

    @property
    def loc(self) -> str:
        return url_for(self._endpoint, _external=True)


class SitemapUrl:
    def __init__(self, endpoint: str, **kwargs) -> None:
        self._endpoint = endpoint
        self._kwargs = kwargs

    @property
    def loc(self) -> str:
        return url_for(self._endpoint, **self._kwargs, _external=True)
