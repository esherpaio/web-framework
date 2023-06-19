from web.mail.base import _send_over_sengrid


class TestSendGrid:
    def test_basic_email(self) -> None:
        _send_over_sengrid(
            from_="contact@enlarge-online.nl",
            to=["contact@enlarge-online.nl"],
            subject="Web Framework unit test",
            html="<p>Web Framework unit test</p>",
        )
