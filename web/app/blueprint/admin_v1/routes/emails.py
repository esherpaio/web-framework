from flask import render_template, request

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.app.bootstrap import get_pages
from web.database import conn
from web.database.model import Email
from web.mail import MailEvent


@admin_v1_bp.get("/admin/emails")
def emails() -> str:
    limit = request.args.get("l", type=int, default=40)
    page = request.args.get("p", type=int, default=1)
    offset = (limit * page) - limit

    with conn.begin() as s:
        count = s.query(Email).filter(Email.event_id == MailEvent.WEBSITE_BULK).count()
        emails_ = (
            s.query(Email)
            .filter(Email.event_id == MailEvent.WEBSITE_BULK)
            .order_by(Email.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    pagination = get_pages(offset, limit, count)
    return render_template(
        "admin/emails.html",
        emails=emails_,
        pagination=pagination,
    )
