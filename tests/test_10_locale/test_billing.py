class TestCreateBilling:
    #
    # Creating
    #

    def test_create_currency(self, post_currency):
        resp = post_currency
        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_create_region(self, post_region):
        resp = post_region
        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_create_country(self, post_country):
        resp = post_country
        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_create_language(self, post_language):
        resp = post_language
        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_create_billing(self, post_billing):
        resp = post_billing
        assert 200 <= resp.status_code <= 299
        assert resp.json

    #
    # Fetching
    #

    def test_get_currency(self, post_currency, client, admin) -> None:
        currency_id = post_currency.json["data"]["id"]
        resp = client.get(f"/api/v1/currencies/{currency_id}", headers={**admin})
        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_get_region(self, post_region, client, admin) -> None:
        region_id = post_region.json["data"]["id"]
        resp = client.get(f"/api/v1/regions/{region_id}", headers={**admin})
        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_get_country(self, post_country, client, user) -> None:
        country_id = post_country.json["data"]["id"]
        resp = client.get(f"/api/v1/countries/{country_id}", headers={**user})
        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_get_billing(self, post_billing, client, user) -> None:
        billing_id = post_billing.json["data"]["id"]
        resp = client.get(f"/api/v1/billings/{billing_id}", headers={**user})
        assert 200 <= resp.status_code <= 299
        assert resp.json

    #
    # Modifying
    #

    def test_patch_billing(self, post_billing, client, user):
        billing_id = post_billing.json["data"]["id"]
        resp = client.patch(
            f"/api/v1/billings/{billing_id}",
            headers={**user},
            json={
                "address": "Beethovenlaan 2",
                "city": "Vlijmen",
                "company": None,
                "email": "stnmertens@gmail.com",
                "first_name": "Stan",
                "last_name": "Mertens",
                "phone": "+31615389916",
                "vat": None,
                "zip_code": "5251HL",
            },
        )
        assert 200 <= resp.status_code <= 299
        assert resp.json

    #
    # Removing
    #

    def test_delete_country(self, post_country, client, admin) -> None:
        country_id = post_country.json["data"]["id"]
        resp = client.delete(f"/api/v1/countries/{country_id}", headers={**admin})
        assert resp.status_code == 409

    def test_delete_currency(self, post_currency, client, admin) -> None:
        currency_id = post_currency.json["data"]["id"]
        resp = client.delete(f"/api/v1/currencies/{currency_id}", headers={**admin})
        assert resp.status_code == 409

    def test_delete_region(self, post_region, client, admin) -> None:
        region_id = post_region.json["data"]["id"]
        resp = client.delete(f"/api/v1/regions/{region_id}", headers={**admin})
        assert resp.status_code == 409
