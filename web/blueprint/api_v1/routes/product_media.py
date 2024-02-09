import os
import re

from flask import request
from werkzeug import Response
from werkzeug.utils import secure_filename

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import File, FileTypeId, Product, ProductMedia, UserRoleLevel
from web.libs import cdn
from web.libs.api import ApiText, json_get, response
from web.libs.auth import access_control

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.post("/products/<int:product_id>/media")
@access_control(UserRoleLevel.ADMIN)
def post_products_id_media(product_id: int) -> Response:
    with conn.begin() as s:
        # Get product
        product = s.query(Product).filter_by(id=product_id).first()
        if not product:
            return response(404, ApiText.HTTP_404)

        # Generate sequence number
        sequence = 1
        if config.CDN_AUTO_NAMING:
            last_media = (
                s.query(ProductMedia)
                .filter_by(product_id=product_id)
                .order_by(ProductMedia.id.desc())
                .first()
            )
            if last_media:
                match = re.search(r"(\d+)\.\w+$", last_media.file.path)
                if match is not None:
                    sequence = int(match.group(1))

        for request_file in request.files.getlist("file"):
            # Increment sequence
            sequence += 1

            # Create details
            if request_file.filename is None:
                continue
            name, extension = os.path.splitext(request_file.filename)
            if config.CDN_AUTO_NAMING:
                name = f"{product.slug}-{sequence}"
            else:
                name = secure_filename(name)
            extension = extension.lstrip(".").lower()
            filename = f"{name}.{extension}"

            # Create CDN path
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

            # Upload media
            cdn.upload(request_file, cdn_path)

            # Insert file and product media
            file = File(path=cdn_path, type_id=type_id)
            s.add(file)
            s.flush()
            product_media = ProductMedia(product_id=product_id, file_id=file.id)
            s.add(product_media)
            s.flush()

    return response()


@api_v1_bp.patch("/products/<int:product_id>/media/<int:media_id>")
@access_control(UserRoleLevel.ADMIN)
def patch_products_id_media_id(product_id: int, media_id: int) -> Response:
    description, has_description = json_get("description", str)
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get product media and file
        product_media = (
            s.query(ProductMedia).filter_by(id=media_id, product_id=product_id).first()
        )
        if not product_media:
            return response(404, ApiText.HTTP_404)
        file = s.query(File).filter_by(id=product_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Update product media and file
        if has_order:
            product_media.order = order
        if has_description:
            file.description = description

    return response()


@api_v1_bp.delete("/products/<int:product_id>/media/<int:media_id>")
@access_control(UserRoleLevel.ADMIN)
def delete_products_id_media_id(product_id: int, media_id) -> Response:
    with conn.begin() as s:
        # Get product media and file
        product_media = (
            s.query(ProductMedia).filter_by(id=media_id, product_id=product_id).first()
        )
        if not product_media:
            return response(404, ApiText.HTTP_404)
        file = s.query(File).filter_by(id=product_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Remove file from CDN
        cdn.delete(file.path)

        # Delete product media and file
        s.delete(file)
        s.delete(product_media)

    return response()


#
# Functions
#
