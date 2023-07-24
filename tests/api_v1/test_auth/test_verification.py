class TestCreateVerification:
    def test_create_billing_currency(self, client):
        resp = client.get("/api/v1/verifications", query_string={"key": "user"})
        print(resp.json)
        assert 200 <= resp.status_code <= 299
        assert resp.json
