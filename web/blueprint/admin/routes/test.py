from flask import render_template
from sqlalchemy.orm import Query, joinedload

from web.blueprint.admin import admin_bp
from web.blueprint.admin._base import Column, Table
from web.database.client import conn
from web.database.model import Category


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


@admin_bp.get("/admin/test")
def test() -> str:
    table = CategoryTable()
    with conn.begin() as s:
        table.query_all(s)
    return render_template("admin/test.html", table=table)
