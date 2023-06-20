import json

from flask import request, url_for
from flask_login import current_user
from markupsafe import Markup

from web import config
from web.database.model import Page


class Schema:
    """A class to generate schema.org JSON-LD."""

    def __init__(self) -> None:
        self._data = None

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, data: dict) -> None:
        for key, value in data.copy().items():
            if value is None:
                data.pop(key)
        self._data = data

    @property
    def tag(self) -> Markup:
        return Markup(
            f"<script type='application/ld+json'>{ json.dumps(self.data) }</script>"
        )


class SchemaWebPage(Schema):
    def __init__(
        self,
        title: str,
        description: str | None = None,
    ) -> None:
        super().__init__()
        self.data = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "url": request.base_url,
            "name": title,
            "description": description,
        }


class SchemaWebsite(Schema):
    def __init__(self) -> None:
        super().__init__()
        home_url = url_for(
            config.ENDPOINT_HOME,
            _locale=current_user.locale,
            _external=True,
        )
        self.data = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "url": home_url,
            "name": config.WEBSITE_NAME,
            "inLanguage": config.WEBSITE_LANGUAGE_CODE,
        }


class SchemaOrganization(Schema):
    def __init__(self) -> None:
        super().__init__()
        home_url = url_for(
            config.ENDPOINT_HOME,
            _locale=current_user.locale,
            _external=True,
        )
        social_urls = [
            config.SOCIAL_DISCORD,
            config.SOCIAL_FACEBOOK,
            config.SOCIAL_INSTAGRAM,
            config.SOCIAL_PINTEREST,
            config.SOCIAL_TWITTER,
            config.SOCIAL_YOUTUBE,
        ]
        self.data = {
            "@context": "https://schema.org",
            "@type": "Corporation",
            "name": config.WEBSITE_NAME,
            "url": home_url,
            "logo": config.WEBSITE_FAVICON_URL,
            "sameAs": [x for x in social_urls if x],
        }


class SchemaPerson(Schema):
    def __init__(
        self,
        name: str,
        title: str,
        image_url: str | None = None,
        social_urls: list[str] | None = None,
    ) -> None:
        super().__init__()
        data = {
            "@context": "https://schema.org/",
            "@type": "Person",
            "name": name,
            "url": request.base_url,
            "jobTitle": title,
            "worksFor": SchemaOrganization().data,
        }
        if image_url:
            data["image"] = image_url
        if social_urls:
            data["sameAs"] = social_urls
        self.data = data


class SchemaProduct(Schema):
    def __init__(
        self,
        name: str,
        price: float,
        image_url: str | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__()
        data = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": name,
            "brand": {
                "@type": "Brand",
                "name": config.BUSINESS_NAME,
            },
            "offers": {
                "@type": "Offer",
                "url": request.base_url,
                "priceCurrency": current_user.currency.code,
                "price": round(price, 2),
                "itemCondition": "https://schema.org/NewCondition",
            },
        }
        if image_url:
            data["image"] = image_url
        if description:
            data["description"] = description
        self.data = data


def gen_schemas(page: Page = None, schemas: list[Schema] | None = None) -> list[Schema]:
    if schemas is None:
        schemas = []
    if isinstance(page, Page):
        if page.endpoint == config.ENDPOINT_HOME:
            schemas.append(SchemaWebsite())
            schemas.append(SchemaOrganization())
        schemas.append(SchemaWebPage(page.name, page.desc))
    return schemas
