import os
import re

from flask import Response, request
from werkzeug.utils import secure_filename

from web import config
from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Article, ArticleMedia, File, FileTypeId, UserRoleLevel
from web.helper import cdn
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/articles/<int:article_id>/media")
def post_articles_id_media(article_id: int) -> Response:
    with conn.begin() as s:
        # Get article
        article = s.query(Article).filter_by(id=article_id).first()
        if not article:
            return response(404, ApiText.HTTP_404)

        # Generate sequence number
        sequence = 1
        if config.CDN_AUTO_NAMING:
            last_media = (
                s.query(ArticleMedia)
                .filter_by(article_id=article_id)
                .order_by(ArticleMedia.id.desc())
                .first()
            )
            if last_media:
                match = re.search(r"(\d+)\D+$", last_media.file.path)
                sequence = int(match.group(1))

        for request_file in request.files.getlist("file"):
            # Increment sequence
            sequence += 1

            # Create details
            name, extension = os.path.splitext(request_file.filename)
            if config.CDN_AUTO_NAMING:
                name = f"{article.slug}-{sequence}"
            else:
                name = secure_filename(name)
            extension = extension.lstrip(".").lower()
            filename = f"{name}.{extension}"

            # Create CDN path
            cdn_path_parts = ["article", article.slug, filename]
            if config.APP_DEBUG:
                cdn_path_parts.insert(0, "_development")
            cdn_path = os.path.join(*cdn_path_parts)

            # Get media type
            if extension in config.CDN_IMAGE_EXTS:
                type_id = FileTypeId.IMAGE
            elif extension in config.CDN_VIDEO_EXTS:
                type_id = FileTypeId.VIDEO
            else:
                continue

            # Upload media
            cdn.upload(request_file, cdn_path)

            # Insert file and article media
            file = File(path=cdn_path, type_id=type_id)
            s.add(file)
            s.flush()
            article_media = ArticleMedia(article_id=article_id, file_id=file.id)
            s.add(article_media)

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/articles/<int:article_id>/media/<int:media_id>")
def patch_articles_id_media_id(article_id: int, media_id: int) -> Response:
    desc, has_desc = json_get("desc", str)
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get article media and file
        article_media = (
            s.query(ArticleMedia).filter_by(id=media_id, article_id=article_id).first()
        )
        if not article_media:
            return response(404, ApiText.HTTP_404)
        file = s.query(File).filter_by(id=article_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Update article media and file
        if has_order:
            article_media.order = order
        if has_desc:
            file.desc = desc

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/articles/<int:article_id>/media/<int:media_id>")
def delete_articles_id_media_id(article_id: int, media_id: int) -> Response:
    with conn.begin() as s:
        # Get article media and file
        article_media = (
            s.query(ArticleMedia).filter_by(id=media_id, article_id=article_id).first()
        )
        if not article_media:
            return response(404, ApiText.HTTP_404)
        file = s.query(File).filter_by(id=article_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Delete file from CDN
        cdn.delete(file.path)

        # Delete article media and file
        s.delete(file)
        s.delete(article_media)

    return response()
