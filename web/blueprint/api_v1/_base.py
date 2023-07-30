from enum import StrEnum
from typing import Any, Callable, Type

from flask import abort, has_request_context, request
from sqlalchemy import Column, ColumnExpressionArgument
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.database.client import conn
from web.database.model import Model
from web.helper.api import ApiText, args_get, json_get, response


class API:
    model: Type[Model] | None = None

    post_columns: set[Column] = set()
    post_message: str | StrEnum | None = None

    patch_columns: set[Column] = set()
    patch_message: str | StrEnum | None = None

    get_args: set[Column] = set()
    get_args_required: set[Column] = set()
    get_columns: set[Column] = set()
    get_message: str | StrEnum | None = None

    delete_message: str | StrEnum | None = None

    #
    # Internal functions
    #

    @staticmethod
    def _gen_request_data(
        columns: set[Column],
    ) -> dict[str, Any]:
        if not has_request_context():
            raise RuntimeError
        if not request.is_json:
            return {}

        request_json = request.json
        if not isinstance(request_json, dict):
            abort(response(400, ApiText.HTTP_400))

        data = {}
        for column in columns:
            if column.name not in request_json:
                continue
            value, _ = json_get(
                column.name,
                column.type.python_type,
                nullable=bool(column.nullable),
                default=column.default,
            )
            data[column.name] = value
        return data

    @classmethod
    def _gen_query_data(
        cls,
        args: set[Column],
        args_required: set[Column] | None = None,
    ) -> dict[str, Any]:
        if not has_request_context():
            raise RuntimeError
        if request.args is None:
            return {}
        if args_required is None:
            args_required = set()

        request_args = request.args.to_dict()
        data = {}
        for arg in args:
            if arg.name not in request_args:
                if arg in args_required:
                    abort(response(400, ApiText.HTTP_400))
                continue
            value, _ = args_get(
                arg.name,
                arg.type.python_type,
                nullable=bool(arg.nullable),
                default=arg.default,
            )
            data[arg.name] = value
        return data

    @classmethod
    def gen_model_data(
        cls,
        models: list[Model],
    ) -> list[dict[str, Any]]:
        data = []
        for model in models:
            model_data = {}
            for attr in cls.get_columns:
                model_data[attr.name] = getattr(model, attr.name)
            data.append(model_data)
        return data

    @classmethod
    def _gen_query_filters(
        cls,
        query_data: dict[str, Any],
    ) -> set[ColumnExpressionArgument[bool]]:
        data = set()
        for key, value in query_data.items():
            filter_ = getattr(cls.model, key) == value
            data.add(filter_)
        return data

    @staticmethod
    def _get_sql_results(
        queries: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> list[Type[Model] | None]:
        results = []
        with conn.begin() as s:
            for model, filters in queries.items():
                result = s.query(model).filter(*filters).first()
                results.append(result)
        return results

    @classmethod
    def _do_calls(
        cls,
        s: Session,
        models: list[Type[Model]] | Type[Model] | list[None] | None,
        data: dict | None,
        calls: list[Callable],
    ) -> None:
        if models is None:
            models = [None]
        elif isinstance(models, Model):
            models = [models]
        for model in models:
            for call in calls:
                call(s, model, data)
                s.flush()

    #
    # Authorization
    #

    @classmethod
    def raise_all_is_none(
        cls,
        sqls: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if all of the queries return None."""
        results = cls._get_sql_results(sqls)
        if all(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_all_is_not_none(
        cls,
        sqls: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if all of the queries return not None."""
        results = cls._get_sql_results(sqls)
        if all(x is not None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_any_is_none(
        cls,
        sqls: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if any of the queries return None."""
        results = cls._get_sql_results(sqls)
        if any(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_any_is_not_none(
        cls,
        sqls: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if any of the queries return not None."""
        results = cls._get_sql_results(sqls)
        if any(x is not None for x in results):
            abort(response(403, ApiText.HTTP_403))

    #
    # Operations
    #

    @classmethod
    def post(
        cls,
        add_request: dict | None = None,
        pre_calls: list[Callable] | None = None,
        post_calls: list[Callable] | None = None,
    ) -> Response:
        # Sanity checks
        if cls.model is None:
            raise NotImplementedError
        if pre_calls is None:
            pre_calls = []
        if post_calls is None:
            post_calls = []

        # Generate data
        data = cls._gen_request_data(cls.post_columns)
        if add_request is not None:
            data.update(add_request)

        # Insert model
        with conn.begin() as s:
            cls._do_calls(s, None, data, pre_calls)
            if data:
                model = cls.model()
                for k, v in data.items():
                    if hasattr(model, k):
                        setattr(model, k, v)
                s.add(model)
            cls._do_calls(s, model, data, post_calls)

        resp_data = cls.gen_model_data([model])[0]
        return response(message=cls.post_message, data=resp_data)

    @classmethod
    def patch(
        cls,
        model_id: int,
        add_request: dict | None = None,
        filters: set[ColumnExpressionArgument[bool]] | None = None,
        post_calls: list[Callable] | None = None,
    ) -> Response:
        # Sanity checks
        if cls.model is None:
            raise NotImplementedError
        if filters is None:
            filters = set()
        if post_calls is None:
            post_calls = []

        # Generate data
        data = cls._gen_request_data(cls.post_columns)
        if add_request is not None:
            data.update(add_request)

        # Patch model
        with conn.begin() as s:
            model = (
                s.query(cls.model).filter(cls.model.id == model_id, *filters).first()
            )
            if model is None:
                abort(response(404, ApiText.HTTP_404))
            for k, v in data.items():
                if hasattr(model, k):
                    setattr(model, k, v)
            s.flush()
            cls._do_calls(s, model, data, post_calls)

        resp_data = cls.gen_model_data([model])[0]
        return response(message=cls.patch_message, data=resp_data)

    @classmethod
    def get(
        cls,
        reference: Type[Model] | int | None = None,
        filters: set[ColumnExpressionArgument[bool]] | None = None,
        post_calls: list[Callable] | None = None,
        as_list: bool = False,
        max_size: int | None = None,
    ) -> Response:
        # Sanity checks
        if cls.model is None:
            raise NotImplementedError
        if filters is None:
            filters = set()
        if post_calls is None:
            post_calls = []

        # Prepare data
        limit = max_size or None
        data = cls._gen_query_data(cls.get_args, cls.get_args_required)
        query_filters = cls._gen_query_filters(data)
        filters = filters.union(query_filters)

        # Parse reference to models
        with conn.begin() as s:
            if reference is None:
                models = s.query(cls.model).filter(*filters).limit(limit).all()
            elif isinstance(reference, int):
                models = [
                    (
                        s.query(cls.model)
                        .filter(cls.model.id == reference, *filters)
                        .first()
                    )
                ]
            elif isinstance(reference, Model):
                models = [reference]
            cls._do_calls(s, models, data, post_calls)

        # Check if model exists
        if not models and not as_list:
            abort(response(404, ApiText.HTTP_404))

        # Create response
        resp_data = cls.gen_model_data(models)
        if as_list:
            resp = response(message=cls.get_message, data=resp_data)
        else:
            resp = response(message=cls.get_message, data=resp_data[0])
        return resp

    @classmethod
    def delete(
        cls,
        model_id: int,
        filters: set[ColumnExpressionArgument[bool]] | None = None,
        pre_calls: list[Callable] | None = None,
        post_calls: list[Callable] | None = None,
    ) -> Response:
        # Sanity checks
        if cls.model is None:
            raise NotImplementedError
        if filters is None:
            filters = set()
        if pre_calls is None:
            pre_calls = []
        if post_calls is None:
            post_calls = []

        # Delete model
        with conn.begin() as s:
            model = (
                s.query(cls.model).filter(cls.model.id == model_id, *filters).first()
            )
            if model is None:
                abort(response(404, ApiText.HTTP_404))
            cls._do_calls(s, model, None, pre_calls)
            s.delete(model)
            cls._do_calls(s, model, None, post_calls)

        return response(message=cls.delete_message)
