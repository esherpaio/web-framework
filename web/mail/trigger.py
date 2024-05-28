from datetime import datetime, timedelta

from sqlalchemy import null, or_

from web.database import conn
from web.database.model import Email, EmailStatusId
from web.libs.logger import log
from web.mail import mail

#
# Functions
#


def send_emails() -> None:
    while True:
        with conn.begin() as s:
            email = (
                s.query(Email)
                .filter(
                    Email.created_at > datetime.utcnow() - timedelta(weeks=1),
                    or_(
                        Email.updated_at == null(),
                        Email.updated_at < datetime.utcnow() - timedelta(days=1),
                    ),
                    Email.status_id.in_([EmailStatusId.QUEUED, EmailStatusId.FAILED]),
                )
                .order_by(Email.id.asc())
                .with_for_update(skip_locked=True)
                .first()
            )
            if not email:
                break
            log.info(f"Triggering email event {email.event_id}")
            mail.trigger_events(s, email.event_id, _email=email, **email.data)


if __name__ == "__main__":
    send_emails()
