import json

from flask import request, url_for
from markupsafe import Markup

from webshop import config
from webshop.database.model import Page


class Schema:
    def __init__(self):
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
    def markup(self) -> Markup:
        return Markup(json.dumps(self.data))


class SchemaWebPage(Schema):
    def __init__(self, title: str, description: str = None) -> None:
        super().__init__()
        self.data = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "@id": f"{request.base_url}#webpage",
            "url": request.base_url,
            "name": title,
            "description": description,
        }


class SchemaWebsite(Schema):
    def __init__(self):
        super().__init__()
        home_url = url_for(config.ENDPOINT_HOME, _external=True)
        self.data = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": f"{home_url}#website",
            "url": home_url,
            "name": config.WEBSITE_NAME,
            "inLanguage": config.WEBSITE_LANGUAGE,
        }


class SchemaOrganization(Schema):
    def __init__(self):
        super().__init__()
        home_url = url_for(config.ENDPOINT_HOME, _external=True)
        self.data = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "@id": f"{home_url}#organization",
            "name": f"{config.WEBSITE_NAME}",
            "url": home_url,
            "logo": config.WEBSITE_FAVICON,
            "sameAs": [
                config.SOCIAL_FACEBOOK,
                config.SOCIAL_INSTAGRAM,
                config.SOCIAL_TWITTER,
                config.SOCIAL_YOUTUBE,
                config.SOCIAL_DISCORD,
            ],
            "contactPoint": [
                {
                    "@type": "ContactPoint",
                    "email": config.BUSINESS_EMAIL,
                    "contactType": "Sales",
                }
            ],
        }


def gen_schemas(page: Page = None) -> list[Schema]:
    schemas = []
    if isinstance(page, Page):
        if page.endpoint == config.ENDPOINT_HOME:
            schemas.append(SchemaWebsite())
            schemas.append(SchemaOrganization())
        schemas.append(SchemaWebPage(page.name, page.desc))
    return schemas
