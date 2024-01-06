from flask import render_template
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
    option_name = "name"


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
    create_columns = [Category.name, Category.order]
    detail = True
    detail_view = "admin.category"
    detail_view_args = {"category_id": Category.id}
    edit = True
    edit_func = "patchCategoriesId"
    edit_columns = [Category.child_id, Category.order, Category.in_header]
    remove = True
    remove_func = "deleteCategoriesId"


@admin_bp.get("/admin/categories")
def categories() -> str:
    table = CategoryTable()
    table.create_func_args = []
    table.edit_func_args = [Category.id]
    table.remove_func_args = [Category.id]
    with conn.begin() as s:
        table.query_all(s)
    return render_template("admin_table.html", table=table)


class CategoryItemSkuColumn(Column):
    query: Query = (
        Query(Sku)
        .options(
            joinedload(Sku.product),
            joinedload(Sku.details),
            joinedload(Sku.details, SkuDetail.option),
            joinedload(Sku.details, SkuDetail.value),
        )
        .filter(Sku.is_deleted == false())
        .order_by(Sku.slug)
    )
    option_name = "name"


class CategoryItemTable(Table):
    name = "category item"
    plural_name = "category items"
    query: Query = (
        Query(CategoryItem)
        .options(
            joinedload(CategoryItem.sku),
            joinedload(CategoryItem.sku, Sku.product),
            joinedload(CategoryItem.sku, Sku.details),
            joinedload(CategoryItem.sku, Sku.details, SkuDetail.value),
        )
        .order_by(CategoryItem.order, CategoryItem.id)
    )
    columns = [
        (CategoryItem.sku_id, CategoryItemSkuColumn()),
        (CategoryItem.order, Column()),
    ]
    create = True
    create_func = "postCategoriesIdItems"
    create_columns = [CategoryItem.sku_id, CategoryItem.order]
    detail = False
    detail_view = None
    edit = True
    edit_func = "patchCategoriesIdItemsId"
    edit_columns = [CategoryItem.order]
    remove = True
    remove_func = "deleteCategoriesIdItemsId"


@admin_bp.get("/admin/categories/<int:category_id>")
def category(category_id: int) -> str | Response:
    table = CategoryItemTable()
    table.create_func_args = [category_id]
    table.edit_func_args = [category_id, CategoryItem.id]
    table.remove_func_args = [category_id, CategoryItem.id]
    with conn.begin() as s:
        filters = {CategoryItem.category_id == category_id}
        table.query_all(s, *filters)
    return render_template("admin_table.html", table=table)
