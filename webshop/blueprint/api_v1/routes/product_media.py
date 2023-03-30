import os
import re

from flask import Response, request
from sqlalchemy.orm import joinedload

from webshop import config
from webshop.blueprint.api_v1 import api_v1_bp
from webshop.database.client import Conn
from webshop.database.model import Product, ProductMedia, File
from webshop.database.model.file_type import FileTypeId
from webshop.database.model.user_role import UserRoleLevel
from webshop.helper import cdn
from webshop.helper.api import response, ApiText, json_get
from webshop.helper.security import authorize
from webshop.helper.validation import gen_slug


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/products/<int:product_id>/media")
def post_product_id_media(product_id: int) -> Response:
    with Conn.begin() as s:
        # Get product
        # Raise if product doesn't exist
        product = s.query(Product).filter_by(id=product_id).first()
        if not product:
            return response(404, ApiText.HTTP_404)

        # Generate sequence number
        last_media = (
            s.query(ProductMedia)
            .options(joinedload(ProductMedia.product))
            .filter_by(product_id=product_id)
            .order_by(ProductMedia.id.desc())
            .first()
        )
        sequence = 1
        if last_media:
            match = re.search(r"(\d+)\D+$", last_media.file.path)
            if match:
                sequence = int(match.group(1))

        for request_file in request.files.getlist("file"):
            # Create details
            product_name = gen_slug(product.name)
            _, extension = os.path.splitext(request_file.filename)
            extension = extension.lstrip(".").lower()
            filename = f"{product_name}-{sequence}.{extension}"

            # Create path
            cdn_path_parts = ["product", product_name, filename]
            if config.APP_DEBUG:
                cdn_path_parts.insert(0, "_debug")
            cdn_path = os.path.join(*cdn_path_parts)

            # Get media type
            if extension in config.EXTENSIONS_IMAGE:
                type_id = FileTypeId.IMAGE
            elif extension in config.EXTENSIONS_VIDEO:
                type_id = FileTypeId.VIDEO
            else:
                continue

            # Upload file
            # Insert media
            cdn.upload(request_file, cdn_path)
            file = File(path=cdn_path, type_id=type_id)
            s.add(file)
            s.flush()

            # Insert product_media
            product_media = ProductMedia(product_id=product_id, file_id=file.id)
            s.add(product_media)
            s.flush()

            # Increment sequence
            sequence += 1

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/products/<int:product_id>/media/<int:media_id>")
def patch_product_id_media_id(product_id: int, media_id: int) -> Response:
    desc, has_desc = json_get("desc", str)
    order, has_order = json_get("order", int)

    with Conn.begin() as s:
        # Get product_media
        # Raise if product_media doesn't exist
        product_media = (
            s.query(ProductMedia).filter_by(id=media_id, product_id=product_id).first()
        )
        if not product_media:
            return response(404, ApiText.HTTP_404)

        # Get media
        # Raise if media doesn't exist
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


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/products/<int:product_id>/media/<int:media_id>")
def delete_media_id(product_id: int, media_id) -> Response:
    with Conn.begin() as s:
        # Get product_media
        # Raise if product_media doesn't exist
        product_media = (
            s.query(ProductMedia).filter_by(id=media_id, product_id=product_id).first()
        )
        if not product_media:
            return response(404, ApiText.HTTP_404)

        # Get media
        # Raise if media doesn't exist
        file = s.query(File).filter_by(id=product_media.file_id).first()
        if not file:
            return response(404, ApiText.HTTP_404)

        # Remove file
        # Delete media and product_media
        cdn.delete(file.path)
        s.delete(file)
        s.delete(product_media)

    return response()
