shipping_id = None


class TestShippingAPI:
    def test_post(self, client, user_headers) -> None:
        resp = client.post(
            "/api/v1/shippings",
            headers={**user_headers},
            json={
                "address": "Eisenhowerlaan 128",
                "city": "Utrecht",
                "company": "Enlarge",
                "country_id": 1,
                "email": "contact@enlarge-online.nl",
                "first_name": "Stan",
                "last_name": "Mertens",
                "phone": "+31615389916",
                "zip_code": "3527HJ",
            },
        )

        assert 200 <= resp.status_code <= 299
        assert resp.json

        global shipping_id
        shipping_id = resp.json["data"]["id"]

    def test_patch(self, client, user_headers) -> None:
        resp = client.patch(
            f"/api/v1/shippings/{shipping_id}",
            headers={**user_headers},
            json={
                "address": "Beethovenlaan 2",
                "city": "Vlijmen",
                "company": None,
                "country_id": 1,
                "email": "stnmertens@gmail.com",
                "first_name": "Stan",
                "last_name": "Mertens",
                "phone": "+31615389916",
                "zip_code": "5251HL",
            },
        )

        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_get(self, client, user_headers) -> None:
        resp = client.get(
            f"/api/v1/shippings/{shipping_id}",
            headers={**user_headers},
        )

        assert 200 <= resp.status_code <= 299
        assert resp.json
