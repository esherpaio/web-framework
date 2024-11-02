from flask import render_template, request
from sqlalchemy.orm import joinedload

from web.app.blueprint import admin_bp
from web.database import conn
from web.database.model import User
from web.ext.bootstrap import get_pages


@admin_bp.get("/admin/users")
def users() -> str:
    search = request.args.get("s", type=str, default="")
    limit = request.args.get("l", type=int, default=40)
    page = request.args.get("p", type=int, default=1)
    offset = (limit * page) - limit

    filters = {User.email.is_not(None)}
    if search:
        filters.add(User.email.ilike(f"%{search}%"))

    with conn.begin() as s:
        users_len = s.query(User).filter(*filters).count()
        users_ = (
            s.query(User)
            .options(joinedload(User.role))
            .filter(*filters)
            .order_by(User.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    pagination = get_pages(offset, limit, users_len)
    return render_template(
        "admin/users.html",
        search=search,
        users=users_,
        pagination=pagination,
    )
