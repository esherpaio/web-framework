from typing import Any

from flask import url_for
from sqlalchemy.orm import Query, Session
from sqlalchemy.orm import QueryableAttribute as QA
from sqlalchemy.orm.attributes import InstrumentedAttribute as IA

from web.database.model import B, Base


class Column:
    query: Query | None = None
    attr_name: str
    user_name: str
    html_id: str
    variant: str
    value: Any
    option_name: str
    nullable: bool

    def __init__(self) -> None:
        self.objects: list[Base] = []

    def query_all(self, s: Session) -> None:
        if self.query is not None:
            self.objects = self.query.with_session(s).all()

    @property
    def options(self) -> list[tuple[str, Base]]:
        return [(getattr(x, self.option_name), x) for x in self.objects]


class Table:
    name: str
    plural_name: str
    query: Query | None = None
    columns: list[tuple[IA | QA, Column]]
    create: bool = False
    create_func: str
    create_func_args: list[IA | int | str] = []
    create_columns: list[IA] = []
    detail: bool = False
    detail_view: str | None
    detail_view_args: dict[str, IA] = {}
    edit: bool = False
    edit_func: str
    edit_func_args: list[IA | str | int] = []
    edit_columns: list[IA] = []
    remove: bool = False
    remove_func: str
    remove_func_args: list[IA | str | int] = []

    def __init__(self) -> None:
        self.func_name = self.get_func_name(self.name)
        self.func_plural_name = self.get_func_name(self.plural_name)
        self.objects: list[Base] = []

    def query_all(self, s: Session, *filters) -> None:
        if self.query is not None:
            self.objects = self.query.filter(*filters).with_session(s).all()
        for _, info in self.columns:
            info.query_all(s)

    def get_func_name(self, name: str) -> str:
        return name.replace(" ", "_")

    @property
    def column_names(self) -> list[str]:
        return [self.column_name(x) for x, _ in self.columns]

    def column_name(self, column) -> str:
        if isinstance(column, IA):
            name = column.name
        elif isinstance(column, QA):
            name = column.key
        parts = name.lower().split("_")
        parts = [x for x in parts if x not in ["id", "in"]]
        return " ".join(parts).title()

    def iter_rows(self) -> list:
        return self.objects

    def get_url(self, row: B) -> str:
        if self.detail_view is None:
            raise NotImplementedError
        kwargs = {}
        for k, v in self.detail_view_args.items():
            if isinstance(v, IA):
                new = getattr(row, v.name)
            else:
                new = v
            kwargs[k] = new
        return url_for(self.detail_view, **kwargs)

    def iter_columns(
        self, row: B | None, *filter_: list[IA]
    ) -> list[tuple[IA | QA, Column]]:
        data = []
        for column, info in self.columns:
            if len(filter_) > 0 and column not in filter_:
                continue
            row_id = row.id if row else None
            if isinstance(column, IA):
                info.attr_name = str(column.name)
                info.variant = self.parse_variant(
                    bool(column.foreign_keys), column.type.python_type
                )
                info.nullable = column.nullable
            elif isinstance(column, QA):
                info.attr_name = str(column.key)
                info.variant = self.parse_variant(False, type(info.value))
                info.nullable = True
            else:
                raise NotImplementedError
            info.value = getattr(row, info.attr_name) if row else None
            info.user_name = self.column_name(column)
            info.html_id = self.element_id(row_id, info.attr_name)
            data.append((column, info))
        return data

    def parse_variant(self, foreign_key: bool, python_type: Any) -> str:
        if foreign_key:
            variant = "foreign_key"
        elif python_type == str:
            variant = "string"
        elif python_type == int:
            variant = "integer"
        elif python_type == float:
            variant = "floating_point"
        elif python_type == bool:
            variant = "boolean"
        else:
            raise NotImplementedError
        return variant

    #
    # HTML elements
    #

    def element_id(self, row_id: int | None, attr_name: str) -> str:
        parts = [self.func_name, attr_name]
        if row_id is not None:
            parts.append(str(row_id))
        return "-".join(parts)

    @property
    def create_modal_id(self) -> str:
        return f"modal-create-{self.func_name}"

    @property
    def create_button_id(self) -> str:
        return f"button-create-{self.func_name}"

    @property
    def create_button_func(self) -> str:
        return f"{self.func_name}Create()"

    def create_button_func_args(self, row: B) -> str:
        args = []
        for arg in self.create_func_args:
            if isinstance(arg, IA):
                args.append(str(getattr(row, arg.name)))
            else:
                args.append(str(arg))
        return ",".join(args)

    def edit_button_id(self, row_id: int | None) -> str:
        parts = ["button-edit", self.func_name]
        if row_id is not None:
            parts.append(str(row_id))
        return "-".join(parts)

    @property
    def edit_button_func(self) -> str:
        return f"{self.func_name}Edit()"

    def edit_button_func_args(self, row: B) -> str:
        args = []
        for arg in self.edit_func_args:
            if isinstance(arg, IA):
                args.append(str(getattr(row, arg.name)))
            else:
                args.append(str(arg))
        return ",".join(args)

    def remove_button_id(self, row_id: int) -> str:
        parts = ["button-remove", self.func_name]
        if row_id is not None:
            parts.append(str(row_id))
        return "-".join(parts)

    @property
    def remove_button_func(self) -> str:
        return f"{self.func_name}Remove()"

    def remove_button_func_args(self, row: B) -> str:
        args = []
        for arg in self.remove_func_args:
            if isinstance(arg, IA):
                args.append(str(getattr(row, arg.name)))
            else:
                args.append(str(arg))
        return ",".join(args)
