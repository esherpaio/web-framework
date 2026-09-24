import hashlib
import json
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from web.database.model import Email, EmailType
from web.setup import config

from .enum import MailEvent


def classify_email(s: Session, event_id: str, data: dict) -> tuple[EmailType, str]:
    digest = _content_hash(event_id, data)
    if is_duplicate(s, digest):
        return EmailType.DUPLICATE, digest
    if is_spam(event_id, data):
        return EmailType.SPAM, digest
    return EmailType.OK, digest


def _content_hash(event_id: str, data: dict) -> str:
    def normalize(value):
        if isinstance(value, str):
            return value.replace("\r\n", "\n").replace("\r", "\n").strip()
        if isinstance(value, dict):
            return {key: normalize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value

    content = json.dumps(
        [event_id, normalize(data)],
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def is_duplicate(s: Session, digest: str) -> bool:
    window_s = config.MAIL_DUPLICATE_WINDOW_S
    since = datetime.now(timezone.utc) - timedelta(seconds=window_s)
    return (
        s.query(Email.id)
        .filter(Email.content_hash == digest, Email.created_at >= since)
        .first()
        is not None
    )


def is_spam(event_id: str, data: dict) -> bool:
    if spam_signature_1(event_id, data):
        return True
    return False


def spam_signature_1(event_id: str, data: dict) -> bool:
    def _detect(value: object) -> bool:
        if not isinstance(value, str):
            return False
        value = value.strip()
        if not re.fullmatch(r"[a-zA-Z]{10,}", value):
            return False
        spaces_count = sum(a.isspace() for a in value)
        transitions = sum(a.isupper() != b.isupper() for a, b in zip(value, value[1:]))
        transitions_perc = transitions / (len(value) - 1)
        return spaces_count == 0 and transitions >= 5 and transitions_perc >= 0.25

    if event_id == MailEvent.WEBSITE_CONTACT:
        name_random = _detect(data.get("name"))
        message_random = _detect(data.get("message"))
        return name_random and message_random
    return False
