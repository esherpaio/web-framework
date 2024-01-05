from flask import redirect, render_template, url_for
from sqlalchemy import false
from sqlalchemy.orm import Query, joinedload
from werkzeug import Response

from web.blueprint.admin import admin_bp
from web.blueprint.admin._base import Column, Table
from web.database.client import conn
from web.database.model import Category, CategoryItem, Sku, SkuDetail


class CategoryChildColumn(Column):
    query: Query = (
        Query(Category)
        .filter_by(is_deleted=False)
        .order_by(Category.order, Category.id)
    )
    option_name = Category.name.name


class CategoryTable(Table):
    name = "category"
    plural_name = "categories"
    query: Query = (
        Query(Category)
        .options(joinedload(Category.child))
        .filter_by(is_deleted=False)
        .order_by(Category.order, Category.id)
    )
    columns = [
        (Category.name, Column()),
        (Category.child_id, CategoryChildColumn()),
        (Category.order, Column()),
        (Category.in_header, Column()),
    ]
    create = True
    create_func = "postCategories"
    create_func_args = []
    create_columns = [Category.name, Category.order]
    detail = True
    detail_view = "admin.category"
    detail_view_args = {"category_id": Category.id}
    edit = True
    edit_func = "patchCategoriesId"
    edit_func_args = [Category.id]
    edit_columns = [Category.child_id, Category.order, Category.in_header]
    remove = True
    remove_func = "deleteCategoriesId"
    remove_func_args = [Category.id]


@admin_bp.get("/admin/categories")
def categories() -> str:
    table = CategoryTable()
    with conn.begin() as s:
        table.query_all(s)
    return render_template("admin_table.html", table=table)


@admin_bp.get("/admin/categories/<int:category_id>")
def category(category_id: int) -> str | Response:
    with conn.begin() as s:
        category_ = s.query(Category).filter_by(id=category_id).first()
        if not category_:
            return redirect(url_for("admin.error"))

        category_items = (
            s.query(CategoryItem)
            .options(
                joinedload(CategoryItem.sku),
                joinedload(CategoryItem.sku, Sku.product),
                joinedload(CategoryItem.sku, Sku.details),
                joinedload(CategoryItem.sku, Sku.details, SkuDetail.value),
            )
            .filter_by(category_id=category_.id)
            .order_by(CategoryItem.order, CategoryItem.id)
            .all()
        )
        available_skus = (
            s.query(Sku)
            .options(
                joinedload(Sku.product),
                joinedload(Sku.details),
                joinedload(Sku.details, SkuDetail.option),
                joinedload(Sku.details, SkuDetail.value),
            )
            .filter(
                Sku.id.not_in([x.sku.id for x in category_items]),
                Sku.is_deleted == false(),
            )
            .order_by(Sku.slug)
            .all()
        )

    return render_template(
        "admin/category.html",
        category=category_,
        category_items=category_items,
        available_skus=available_skus,
    )
