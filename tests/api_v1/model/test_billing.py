Shipping_id = None


class TestShipping:
    def test_post(self, client, user_headers) -> None:
        resp = client.post(
            "/api/v1/Shippings",
            json={
                "address": "Eisenhowerlaan 128",
                "city": "Utrecht",
                "company": "Enlarge",
                "country_id": 1,
                "email": "contact@enlarge-online.nl",
                "first_name": "Stan",
                "last_name": "Mertens",
                "phone": "+31615389916",
                "vat": "NL002329215B02",
                "zip_code": "3527HJ",
            },
            headers={**user_headers},
        )

        assert 200 <= resp.status_code <= 299
        assert resp.json

        global Shipping_id
        Shipping_id = resp.json["data"]["id"]

    def test_patch(self, client, user_headers) -> None:
        resp = client.patch(
            f"/api/v1/Shippings/{Shipping_id}",
            json={
                "address": "Beethovenlaan 2",
                "city": "Vlijmen",
                "company": None,
                "country_id": 1,
                "email": "stnmertens@gmail.com",
                "first_name": "Stan",
                "last_name": "Mertens",
                "phone": "+31615389916",
                "vat": None,
                "zip_code": "5251HL",
            },
            headers={**user_headers},
        )

        assert 200 <= resp.status_code <= 299
        assert resp.json

    def test_get(self, client, user_headers) -> None:
        resp = client.get(f"/api/v1/Shippings/{Shipping_id}", headers={**user_headers})

        assert 200 <= resp.status_code <= 299
        assert resp.json
