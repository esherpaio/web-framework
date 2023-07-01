import os
import re

from flask import Response, request
from werkzeug.utils import secure_filename

from web import config
from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import File, FileTypeId, Product, ProductMedia, UserRoleLevel
from web.helper import cdn
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/products/<int:product_id>/media")
def post_products_id_media(product_id: int) -> Response:
    with conn.begin() as s:
        # Get product
        # Raise if product doesn't exist
        product = s.query(Product).filter_by(id=product_id).first()
        if not product:
            return response(404, ApiText.HTTP_404)

        # Generate sequence number for CDN_AUTO_NAMING
        sequence = 1
        if config.CDN_AUTO_NAMING:
            last_media = (
                s.query(ProductMedia)
                .filter_by(product_id=product_id)
                .order_by(ProductMedia.id.desc())
                .first()
            )
            if last_media:
                match = re.search(r"(\d+)\D+$", last_media.file.path)
                sequence = int(match.group(1)) + 1

        for request_file in request.files.getlist("file"):
            # Create details
            name, extension = os.path.splitext(request_file.filename)
            if config.CDN_AUTO_NAMING:
                name = f"{product.slug}-{sequence}"
            else:
                name = secure_filename(name)
            extension = extension.lstrip(".").lower()
            filename = f"{name}.{extension}"

            # Create path
            cdn_path_parts = ["product", product.slug, filename]
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

            # Insert product_media
            product_media = ProductMedia(product_id=product_id, file_id=file.id)
            s.add(product_media)
            s.flush()

            # Increment sequence for CDN_AUTO_NAMING
            sequence += 1

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/products/<int:product_id>/media/<int:media_id>")
def patch_products_id_media_id(product_id: int, media_id: int) -> Response:
    desc, has_desc = json_get("desc", str)
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get product_media
        # Raise if product_media doesn't exist
        product_media = (
            s.query(ProductMedia).filter_by(id=media_id, product_id=product_id).first()
        )
        if not product_media:
            return response(404, ApiText.HTTP_404)

        # Get file
        # Raise if file doesn't exist
        file = s.query(File).filter_by(id=product_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Update order
        if has_order:
            product_media.order_ = order

        # Update desc
        if has_desc:
            file.desc = desc

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/products/<int:product_id>/media/<int:media_id>")
def delete_products_id_media_id(product_id: int, media_id) -> Response:
    with conn.begin() as s:
        # Get product_media
        # Raise if product_media doesn't exist
        product_media = (
            s.query(ProductMedia).filter_by(id=media_id, product_id=product_id).first()
        )
        if not product_media:
            return response(404, ApiText.HTTP_404)

        # Get file
        # Raise if file doesn't exist
        file = s.query(File).filter_by(id=product_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Remove file
        # Delete file and product_media
        cdn.delete(file.path)
        s.delete(file)
        s.delete(product_media)

    return response()
