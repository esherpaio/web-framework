class TestCart:
    #
    # Creating
    #

    def test_post_cart(self, post_cart):
        resp = post_cart
        assert 200 <= resp.status_code <= 299
        assert resp.json

    #
    # Fetching
    #

    def test_get_cart(self, client, user) -> None:
        resp = client.get("/api/v1/carts", headers={**user})
        assert 200 <= resp.status_code <= 299
        assert resp.json

    #
    # Modifying
    #

    def test_patch_cart(self, post_cart, post_billing, client, user):
        cart_id = post_cart.json["data"]["id"]
        billing_id = post_billing.json["data"]["id"]
        resp = client.patch(
            f"/api/v1/carts/{cart_id}",
            headers={**user},
            json={"billing_id": billing_id},
        )
        assert 200 <= resp.status_code <= 299
        assert resp.json
        assert resp.json["data"]["billing_id"] == billing_id
