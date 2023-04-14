from flask import Response

from webshop.blueprint.api_v1 import api_v1_bp
from webshop.blueprint.api_v1.utils.article import clean_html
from webshop.database.client import Conn
from webshop.database.model.article import Article
from webshop.database.model.user_role import UserRoleLevel
from webshop.helper.api import response, ApiText, json_get
from webshop.helper.security import authorize
from webshop.helper.validation import gen_slug


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/articles")
def post_articles() -> Response:
    name, _ = json_get("name", str, nullable=False)

    with Conn.begin() as s:
        # Get article
        # Restore if article is deleted
        # Raise if article is not deleted
        article = s.query(Article).filter_by(slug=gen_slug(name)).first()
        if article:
            if article.is_deleted:
                article.is_deleted = False
            else:
                return response(409, ApiText.HTTP_409)

        else:
            # Insert article
            article = Article(name=name)
            s.add(article)
            s.flush()

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/articles/<int:article_id>")
def patch_articles_id(article_id: int) -> Response:
    html, has_html = json_get("html", str)
    name, has_name = json_get("name", str)
    summary, has_summary = json_get("summary", str)
    is_visible, has_is_visible = json_get("is_visible", bool)

    with Conn.begin() as s:
        # Get article
        # Raise if article doesn't exist
        article = s.query(Article).filter_by(id=article_id).first()
        if article is None:
            return response(404, ApiText.HTTP_404)

        # Update article
        if has_name:
            article.name = name
        if has_summary:
            article.summary = summary
        if has_html:
            article.html = clean_html(html)
        if has_is_visible:
            article.is_visible = is_visible

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/articles/<int:article_id>")
def delete_articles_id(article_id: int) -> Response:
    with Conn.begin() as s:
        # Get article
        # Raise if article doesn't exist
        article = s.query(Article).filter_by(id=article_id).first()
        if not article:
            return response(404, ApiText.HTTP_404)

        # Update is_deleted
        article.is_deleted = True

    return response()
