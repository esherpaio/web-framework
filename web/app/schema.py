import json

from flask import request
from markupsafe import Markup

from web.api import JsonEncoder
from web.app.urls import parse_url
from web.config import config
from web.database.model import AppRoute
from web.locale import current_locale, url_for_locale


class Schema:
    """A class to generate schema.org JSON-LD."""

    def __init__(self) -> None:
        self._data: dict = {}

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
        value = json.dumps(self.data, cls=JsonEncoder)
        return Markup(f"<script type='application/ld+json'>{value}</script>")


class SchemaWebPage(Schema):
    def __init__(
        self,
        title: str | None = None,
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
        home_url = parse_url(
            config.ENDPOINT_HOME,
            _func=url_for_locale,
            _external=True,
            _locale=current_locale.locale,
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
        home_url = parse_url(
            config.ENDPOINT_HOME,
            _func=url_for_locale,
            _external=True,
            _locale=current_locale.locale,
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
            "@context": "https://schema.org/Corporation",
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
            "@context": "https://schema.org/Person",
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
        sku: str | None = None,
        stock: int | None = None,
        image_url: str | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__()
        data = {
            "@context": "https://schema.org/Product",
            "@type": "Product",
            "name": name,
            "brand": {
                "@type": "Brand",
                "name": config.BUSINESS_NAME,
            },
            "offers": {
                "@type": "Offer",
                "url": request.base_url,
                "price": round(price, 2),
                "priceCurrency": current_locale.currency.code,
                "itemCondition": "https://schema.org/NewCondition",
            },
        }
        if sku is not None:
            data["sku"] = sku
        if stock is not None:
            if stock > 0:
                availability = "https://schema.org/InStock"
            else:
                availability = "https://schema.org/OutOfStock"
            data["offers"]["availability"] = availability  # type: ignore[index]
        if image_url is not None:
            data["image"] = image_url
        if description is not None:
            data["description"] = description
        self.data = data


def gen_schemas(
    route: AppRoute | None = None, schemas: list[Schema] | None = None
) -> list[Schema]:
    if schemas is None:
        schemas = []
    if isinstance(route, AppRoute):
        if route.endpoint == config.ENDPOINT_HOME:
            schemas.append(SchemaWebsite())
            schemas.append(SchemaOrganization())
        schemas.append(SchemaWebPage(route.name, route.description))
    return schemas
