class TestCreateVerification:
    #
    # Create user
    #

    def test_post_user(self, post_user):
        resp = post_user
        assert 200 <= resp.status_code <= 299
        assert resp.json

    #
    # Get user
    #

    def test_get_user(self, post_user, client, user) -> None:
        email = post_user.json["data"]["email"]
        resp = client.get(
            "/api/v1/users",
            query_string={"email": email},
            headers={**user},
        )
        assert 200 <= resp.status_code <= 299
        assert resp.json
