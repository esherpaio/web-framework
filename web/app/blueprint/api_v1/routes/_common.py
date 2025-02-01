import uuid

from sqlalchemy.orm import Session

from web.app.urls import parse_url, url_for
from web.config import config
from web.database.model import User, Verification
from web.mail import MailEvent, mail


def recover_user_password(s: Session, user: User) -> None:
    # Insert verification
    key = str(uuid.uuid4())
    verification = Verification(user_id=user.id, key=key)
    s.add(verification)
    s.flush()

    # Send email
    reset_url = parse_url(
        config.ENDPOINT_PASSWORD,
        _func=url_for,
        _external=True,
        verification_key=verification.key,
    )
    mail.trigger_events(
        s,
        MailEvent.USER_REQUEST_PASSWORD,
        email=user.email,
        reset_url=reset_url,
    )
