from typing import Any, Callable, Generic, TypeVar

from flask import abort, has_request_context, request
from psycopg2.errors import UniqueViolation
from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.session import Session

from web.database.model import Base
from web.logger import log

from .utils import ApiText, args_get, json_get, json_response

B = TypeVar("B", bound=Base)


class API(Generic[B]):
    model: B | None = None
    post_columns: set[InstrumentedAttribute | str] = set()
    patch_columns: set[InstrumentedAttribute | str] = set()
    get_filters: set[InstrumentedAttribute | str] = set()
    get_columns: set[InstrumentedAttribute | str] = set()

    #
    # Parsing
    #

    @staticmethod
    def parse_column(
        data: dict,
        column: InstrumentedAttribute | str,
        func: Callable,
    ) -> tuple[str | None, Any]:
        key, value = None, None
        if isinstance(column, InstrumentedAttribute):
            if column.name in data:
                key = column.name
                value, _ = func(
                    key,
                    column.type.python_type,
                    nullable=column.nullable,
                    default=column.default,
                    column=column,
                )
        elif isinstance(column, str):
            if column in data:
                key = column
                value = data.get(column)
        return key, value

    @classmethod
    def gen_data(
        cls,
        columns: set[InstrumentedAttribute | str],
        include_json: bool = True,
        include_path: bool = True,
        include_query: bool = False,
    ) -> dict[str, Any]:
        data = {}
        if include_json:
            data.update(cls.gen_json_data(columns))
        if include_path:
            data.update(cls.gen_path_data())
        if include_query:
            data.update(cls.gen_query_data(columns))
        return data

    @classmethod
    def gen_json_data(cls, columns: set[InstrumentedAttribute | str]) -> dict[str, Any]:
        if not has_request_context():
            raise RuntimeError
        if not request.is_json:
            return {}
        request_json = request.json
        if not isinstance(request_json, dict):
            abort(json_response(400, ApiText.HTTP_400))
        data = {}
        for column in columns:
            key, value = cls.parse_column(request_json, column, json_get)
            if key is not None:
                data[key] = value
        return data

    @staticmethod
    def gen_path_data() -> dict[str, Any]:
        if not has_request_context():
            raise RuntimeError
        if request.view_args is None:
            return {}
        return request.view_args

    @classmethod
    def gen_query_data(cls, args: set[InstrumentedAttribute | str]) -> dict[str, Any]:
        if not has_request_context():
            raise RuntimeError
        if request.args is None:
            return {}
        request_args = request.args.to_dict()
        data = {}
        for arg in args:
            key, value = cls.parse_column(request_args, arg, args_get)
            if key is not None:
                data[key] = value
        return data

    #
    # Resources
    #

    @classmethod
    def gen_resource(cls, s: Session, model: B) -> dict[str, Any]:
        data = {}
        for attr in cls.get_columns:
            if isinstance(attr, InstrumentedAttribute):
                key, value = attr.name, getattr(model, attr.name)
            elif isinstance(attr, str):
                key, value = attr, getattr(model, attr)
            else:
                log.warning(f"Unknown attribute: {attr}")
                continue
            data[key] = value
        return data

    @classmethod
    def gen_resources(cls, s: Session, models: list[B]) -> list[dict[str, Any]]:
        data = []
        for model in models:
            model_data = cls.gen_resource(s, model)
            data.append(model_data)
        return data

    #
    # Query generation
    #

    @classmethod
    def gen_query_filters(
        cls,
        query_data: dict[str, Any],
        required: bool = False,
    ) -> set[ColumnExpressionArgument[bool]]:
        filters = set()
        for key, value in query_data.items():
            if not hasattr(cls.model, key):
                continue
            filter_ = getattr(cls.model, key) == value
            filters.add(filter_)
        if required and not filters:
            abort(json_response(400, ApiText.HTTP_400))
        return filters

    #
    # Database
    #

    @staticmethod
    def insert(s: Session, data: dict, model: B) -> None:
        for k, v in data.items():
            if hasattr(model, k):
                setattr(model, k, v)
        try:
            s.add(model)
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                abort(json_response(409, ApiText.HTTP_409))
            raise e
        s.flush()

    @classmethod
    def get(
        cls,
        s: Session,
        id_: int | None,
        *filters: ColumnExpressionArgument[bool],
    ) -> B:
        if cls.model is None:
            raise NotImplementedError
        if id_ is not None:
            filters += (cls.model.id == id_,)
        model = s.query(cls.model).filter(*filters).first()
        if model is None:
            abort(json_response(404, ApiText.HTTP_404))
        else:
            return model

    @classmethod
    def list_(
        cls,
        s: Session,
        *filters: ColumnExpressionArgument[bool],
        limit: int | None = None,
        offset: int | None = None,
        order_by: InstrumentedAttribute | None = None,
    ) -> list[B]:
        if cls.model is None:
            raise NotImplementedError
        if order_by is None:
            order_by = cls.model.id
        models = (
            s.query(cls.model)
            .filter(*filters)
            .order_by(order_by)
            .limit(limit)
            .offset(offset)
            .all()
        )
        return models

    @staticmethod
    def update(s: Session, data: dict, model: B) -> None:
        for k, v in data.items():
            if hasattr(model, k):
                setattr(model, k, v)
        s.flush()

    @staticmethod
    def delete(s: Session, model: B) -> None:
        s.delete(model)
        s.flush()
