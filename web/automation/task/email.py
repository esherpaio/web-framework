from datetime import datetime, timedelta, timezone

from sqlalchemy import null, or_
from sqlalchemy.orm import Session

from web.database import conn
from web.database.model import Email, EmailStatusId
from web.logger import log
from web.mail import mail

from ..automator import Processor


class EmailProcessor(Processor):
    @classmethod
    def run(cls) -> None:
        cls.log_start()
        with conn.begin() as s:
            cls.send_email(s, max_weeks=4)

    @staticmethod
    def send_email(s: Session, max_weeks: int = 4) -> Email | None:
        email = (
            s.query(Email)
            .filter(
                Email.created_at
                > datetime.now(timezone.utc) - timedelta(weeks=max_weeks),
                or_(
                    Email.updated_at == null(),
                    Email.updated_at < datetime.now(timezone.utc) - timedelta(days=1),
                ),
                Email.status_id.in_([EmailStatusId.QUEUED, EmailStatusId.FAILED]),
            )
            .order_by(Email.id.asc())
            .with_for_update(skip_locked=True)
            .first()
        )
        if email is None:
            return None
        log.info(f"Triggering email event {email.event_id} for user {email.user_id}")
        mail.trigger_events(s, email.event_id, _email=email, **email.data)
        return email
