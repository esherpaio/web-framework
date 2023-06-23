import os
import re

from flask import Response, request
from werkzeug.utils import secure_filename

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Article, ArticleMedia, File, FileTypeId, UserRoleLevel
from web.helper import cdn
from web.helper.api import ApiText, authorize, json_get, response


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/articles/<int:article_id>/media")
def post_articles_id_media(article_id: int) -> Response:
    with conn.begin() as s:
        # Get article
        # Raise if article doesn't exist
        article = s.query(Article).filter_by(id=article_id).first()
        if not article:
            return response(404, ApiText.HTTP_404)

        # Generate sequence number for CDN_AUTO_NAMING
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
            # Create details
            name, extension = os.path.splitext(request_file.filename)
            if config.CDN_AUTO_NAMING:
                name = f"{article.slug}-{sequence}"
            else:
                name = secure_filename(name)
            extension = extension.lstrip(".").lower()
            filename = f"{name}.{extension}"

            # Create path
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

            # Upload file
            # Insert file
            cdn.upload(request_file, cdn_path)
            file = File(path=cdn_path, type_id=type_id)
            s.add(file)
            s.flush()

            # Insert article_media
            article_media = ArticleMedia(article_id=article_id, file_id=file.id)
            s.add(article_media)
            s.flush()

            # Increment sequence for CDN_AUTO_NAMING
            sequence += 1

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/articles/<int:article_id>/media/<int:media_id>")
def patch_articles_id_media_id(article_id: int, media_id: int) -> Response:
    desc, has_desc = json_get("desc", str)
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get article_media
        # Raise if article_media doesn't exist
        article_media = (
            s.query(ArticleMedia).filter_by(id=media_id, article_id=article_id).first()
        )
        if not article_media:
            return response(404, ApiText.HTTP_404)

        # Get file
        # Raise if file doesn't exist
        file = s.query(File).filter_by(id=article_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Update order
        if has_order:
            article_media.order_ = order

        # Update desc
        if has_desc:
            file.desc = desc

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/articles/<int:article_id>/media/<int:media_id>")
def delete_articles_id_media_id(article_id: int, media_id: int) -> Response:
    with conn.begin() as s:
        # Get article_media
        # Raise if article_media doesn't exist
        article_media = (
            s.query(ArticleMedia).filter_by(id=media_id, article_id=article_id).first()
        )
        if not article_media:
            return response(404, ApiText.HTTP_404)

        # Get file
        # Raise if file doesn't exist
        file = s.query(File).filter_by(id=article_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Remove file
        # Delete file and article_media
        cdn.delete(file.path)
        s.delete(file)
        s.delete(article_media)

    return response()
