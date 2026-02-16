import json
from enum import StrEnum
from typing import Any, NotRequired, TypedDict

from flask import request
from markupsafe import Markup

from web.api import JsonEncoder
from web.app.urls import parse_url
from web.database.model import AppRoute
from web.locale import current_locale, url_for_locale
from web.setup import config


class SchemaId(StrEnum):
    WEBSITE = "#website"
    ORGANIZATION = "#organization"
    LOCALBUSINESS = "#localbusiness"
    WEBPAGE = "#webpage"


class ListItem(TypedDict):
    name: str
    description: str
    url: str
    image: NotRequired[str]


class BreadcrumbItem(TypedDict):
    name: str
    url: str


class FaqItem(TypedDict):
    question: str
    answer: str


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
        home_url = parse_url(
            config.ENDPOINT_HOME,
            _func=url_for_locale,
            _external=True,
            _locale=current_locale.locale,
        )
        self.data = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "@id": f"{request.base_url}{SchemaId.WEBPAGE}",
            "url": request.base_url,
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{home_url}{SchemaId.WEBSITE}"},
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
        data = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": f"{home_url}{SchemaId.WEBSITE}",
            "url": home_url,
            "name": config.META_WEBSITE_NAME,
            "inLanguage": current_locale.language_code,
            "publisher": {"@id": f"{home_url}{SchemaId.ORGANIZATION}"},
        }
        if config.ENDPOINT_SEARCH:
            search_url = parse_url(
                config.ENDPOINT_SEARCH,
                _func=url_for_locale,
                _external=True,
                _locale=current_locale.locale,
            )
            data["potentialAction"] = {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{search_url}?s={{search}}",
                },
                "query-input": "required name=search",
            }
        self.data = data


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
            "@context": "https://schema.org",
            "@type": "Organization",
            "@id": f"{home_url}{SchemaId.ORGANIZATION}",
            "name": config.META_WEBSITE_NAME,
            "url": home_url,
            "logo": {
                "@type": "ImageObject",
                "url": config.META_LOGO_URL,
                "caption": f"{config.META_WEBSITE_NAME} Logo",
            },
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
        home_url = parse_url(
            config.ENDPOINT_HOME,
            _func=url_for_locale,
            _external=True,
            _locale=current_locale.locale,
        )
        data = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": name,
            "url": request.base_url,
            "jobTitle": title,
            "worksFor": {"@id": f"{home_url}{SchemaId.ORGANIZATION}"},
        }
        if image_url:
            data["image"] = {
                "@type": "ImageObject",
                "url": image_url,
                "caption": name,
            }
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
        home_url = parse_url(
            config.ENDPOINT_HOME,
            _func=url_for_locale,
            _external=True,
            _locale=current_locale.locale,
        )
        data = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "brand": {
                "@type": "Brand",
                "name": config.META_BRAND_NAME,
            },
            "offers": {
                "@type": "Offer",
                "url": request.base_url,
                "price": round(price, 2),
                "priceCurrency": current_locale.currency.code,
                "itemCondition": "https://schema.org/NewCondition",
                "seller": {"@id": f"{home_url}{SchemaId.ORGANIZATION}"},
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
            data["image"] = {
                "@type": "ImageObject",
                "url": image_url,
                "caption": name,
            }
        if description is not None:
            data["description"] = description
        self.data = data


class SchemaLocalBusiness(Schema):
    def __init__(self) -> None:
        super().__init__()
        home_url = parse_url(
            config.ENDPOINT_HOME,
            _func=url_for_locale,
            _external=True,
            _locale=current_locale.locale,
        )
        data = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "@id": f"{home_url}{SchemaId.LOCALBUSINESS}",
            "name": config.BUSINESS_NAME,
            "email": config.BUSINESS_EMAIL,
            "url": home_url,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": config.BUSINESS_STREET,
                "addressLocality": config.BUSINESS_CITY,
                "postalCode": config.BUSINESS_ZIP_CODE,
                "addressCountry": config.BUSINESS_COUNTRY_CODE,
            },
            "logo": {
                "@type": "ImageObject",
                "url": config.BUSINESS_LOGO_URL,
                "caption": f"{config.BUSINESS_NAME} Logo",
            },
        }
        self.data = data


class SchemaItemList(Schema):
    def __init__(
        self,
        name: str,
        items: list[ListItem],
        description: str,
    ) -> None:
        super().__init__()
        list_items = []
        for position, item in enumerate(items, 1):
            thing: dict[str, Any] = {
                "name": item["name"],
                "description": item["description"],
                "url": item["url"],
            }
            if "image" in item:
                thing["image"] = {
                    "@type": "ImageObject",
                    "url": item["image"],
                    "caption": item["name"],
                }
            list_item = {
                "@type": "ListItem",
                "position": position,
                "item": thing,
            }
            list_items.append(list_item)
        data = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": name,
            "description": description,
            "url": request.base_url,
            "numberOfItems": len(items),
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "itemListElement": list_items,
        }
        self.data = data


class SchemaBreadcrumbList(Schema):
    def __init__(self, items: list[BreadcrumbItem]) -> None:
        super().__init__()
        list_items = []
        for position, item in enumerate(items, 1):
            list_items.append(
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": item["name"],
                    "item": item["url"],
                }
            )
        self.data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": list_items,
        }


class SchemaFaqPage(Schema):
    def __init__(self, items: list[FaqItem]) -> None:
        super().__init__()
        faq_items = []
        for faq in items:
            faq_items.append(
                {
                    "@type": "Question",
                    "name": faq["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq["answer"],
                    },
                }
            )
        self.data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items,
        }


def gen_schemas(
    route: AppRoute | None = None,
    schemas: list[Schema] | None = None,
) -> list[Schema]:
    if schemas is None:
        schemas = []
    if isinstance(route, AppRoute):
        if route.endpoint == config.ENDPOINT_HOME:
            schemas.append(SchemaWebsite())
            schemas.append(SchemaOrganization())
        schemas.append(SchemaWebPage(route.name, route.description))
    return schemas
