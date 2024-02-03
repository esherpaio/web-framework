import pytest

#
# Locale related
#


@pytest.fixture(scope="package")
def post_currency(client, admin) -> dict:
    return client.post(
        "/api/v1/currencies",
        headers={**admin},
        json={
            "code": "EUR",
            "rate": 1.0,
            "symbol": "€",
        },
    )


@pytest.fixture(scope="package")
def post_region(client, admin) -> dict:
    return client.post(
        "/api/v1/regions",
        headers={**admin},
        json={
            "name": "Europe",
        },
    )


@pytest.fixture(scope="package")
def post_country(client, admin, post_currency, post_region) -> dict:
    currency_id = post_currency.json["data"]["id"]
    region_id = post_region.json["data"]["id"]
    return client.post(
        "/api/v1/countries",
        headers={**admin},
        json={
            "code": "NL",
            "in_sitemap": False,
            "name": "the Netherlands",
            "currency_id": currency_id,
            "region_id": region_id,
        },
    )


@pytest.fixture(scope="package")
def post_language(client, admin) -> dict:
    return client.post(
        "/api/v1/languages",
        headers={**admin},
        json={
            "code": "nl",
            "in_sitemap": False,
            "name": "Dutch",
        },
    )


#
# User details
#


@pytest.fixture(scope="package")
def post_billing(post_country, client, user) -> dict:
    country_id = post_country.json["data"]["id"]
    return client.post(
        "/api/v1/billings",
        headers={**user},
        json={
            "address": "Eisenhowerlaan 128",
            "city": "Utrecht",
            "company": "eSherpa",
            "country_id": country_id,
            "email": "contact@esherpa.io",
            "first_name": "Stan",
            "last_name": "Mertens",
            "phone": "+31615389916",
            "vat": "NL002329215B02",
            "zip_code": "3527HJ",
        },
    )


@pytest.fixture(scope="package")
def post_shipping(post_country, client, user) -> dict:
    country_id = post_country.json["data"]["id"]
    return client.post(
        "/api/v1/shippings",
        headers={**user},
        json={
            "address": "Eisenhowerlaan 128",
            "city": "Utrecht",
            "company": "eSherpa",
            "country_id": country_id,
            "email": "contact@esherpa.io",
            "first_name": "Stan",
            "last_name": "Mertens",
            "phone": "+31615389916",
            "zip_code": "3527HJ",
        },
    )


#
# Users
#


@pytest.fixture(scope="package")
def post_user(client, user) -> dict:
    return client.post(
        "/api/v1/users",
        headers={**user},
        json={
            "email": "contact@esherpa.io",
            "password": "password",
            "password_eval": "password",
        },
    )


#
# Cart
#


@pytest.fixture(scope="package")
def post_cart(client, user) -> dict:
    return client.post(
        "/api/v1/carts",
        headers={**user},
    )
