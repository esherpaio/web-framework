from enum import StrEnum
from typing import Any, Callable, Type

from flask import abort, has_request_context, request
from sqlalchemy import Column, ColumnExpressionArgument
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.database.client import conn
from web.database.model import Model
from web.helper.api import ApiText, args_get, json_get, response
from web.helper.logger import logger


class API:
    model: Type[Model] | None = None
    post_columns: set[Column] = set()
    post_message: str | StrEnum | None = None
    patch_columns: set[Column] = set()
    patch_message: str | StrEnum | None = None
    get_args: set[Column] = set()
    get_columns: set[Column | str] = set()
    get_message: str | StrEnum | None = None
    delete_message: str | StrEnum | None = None

    #
    # Parsing data
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
    ) -> dict[str, Any]:
        if not has_request_context():
            raise RuntimeError
        if request.args is None:
            return {}

        request_args = request.args.to_dict()
        data = {}
        for arg in args:
            if arg.name not in request_args:
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
    def _gen_resource_data(
        cls,
        s: Session,
        models: list[Type[Model]],
    ) -> list[dict[str, Any]]:
        data = []
        for model in models:
            model_data: dict[str, Any] = {}
            for attr in cls.get_columns:
                if isinstance(attr, InstrumentedAttribute):
                    key, value = attr.name, getattr(model, attr.name)
                elif isinstance(attr, str):
                    key, value = attr, getattr(model, attr)
                else:
                    logger.warning(f"Unknown attribute: {attr}")
                    continue
                model_data[key] = value
            data.append(model_data)
        return data

    #
    # Query generation
    #

    @classmethod
    def _gen_query_filters(
        cls,
        query_data: dict[str, Any],
    ) -> set[ColumnExpressionArgument[bool]]:
        filters = set()
        for key, value in query_data.items():
            filter_ = getattr(cls.model, key) == value
            filters.add(filter_)
        return filters

    @staticmethod
    def _get_query_results(
        queries: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> list[Type[Model] | None]:
        results = []
        with conn.begin() as s:
            for model, filters in queries.items():
                result = s.query(model).filter(*filters).first()
                results.append(result)
        return results

    #
    # Functions
    #

    @classmethod
    def _get_model(
        cls,
        s: Session,
        id_: int,
        filters: set[ColumnExpressionArgument[bool]],
    ) -> Type[Model]:
        if cls.model is None:
            raise NotImplementedError

        model = s.query(cls.model).filter(cls.model.id == id_, *filters).first()
        if model is None:
            abort(response(404, ApiText.HTTP_404))
        return model

    @classmethod
    def _call(
        cls,
        s: Session,
        calls: list[Callable],
        data: dict | None = None,
        models: list[Type[Model]] | Type[Model] | list[None] | None = None,
        *parent_models: Type[Model],
    ) -> None:
        if models is None:
            models = [None]
        elif isinstance(models, Model):
            models = [models]

        for model in models:
            for call in calls:
                call(s, data, *parent_models, model)
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
        results = cls._get_query_results(sqls)
        if all(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_all_is_not_none(
        cls,
        sqls: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if all of the queries return not None."""
        results = cls._get_query_results(sqls)
        if all(x is not None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_any_is_none(
        cls,
        sqls: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if any of the queries return None."""
        results = cls._get_query_results(sqls)
        if any(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_any_is_not_none(
        cls,
        sqls: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if any of the queries return not None."""
        results = cls._get_query_results(sqls)
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
        # Checks and parsing
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
            model = cls.model()
            cls._call(s, pre_calls, data, model)
            for k, v in data.items():
                if hasattr(model, k):
                    setattr(model, k, v)
            s.add(model)
            s.flush()
            cls._call(s, post_calls, data, model)
            resource = cls._gen_resource_data(s, [model])[0]

        # Return response
        return response(message=cls.post_message, data=resource)

    @classmethod
    def patch(
        cls,
        model_id: int,
        add_request: dict | None = None,
        filters: set[ColumnExpressionArgument[bool]] | None = None,
        pre_calls: list[Callable] | None = None,
        post_calls: list[Callable] | None = None,
    ) -> Response:
        # Checks and parsing
        if cls.model is None:
            raise NotImplementedError
        if filters is None:
            filters = set()
        if pre_calls is None:
            pre_calls = []
        if post_calls is None:
            post_calls = []

        # Generate data
        data = cls._gen_request_data(cls.patch_columns)
        if add_request is not None:
            data.update(add_request)

        # Update model
        with conn.begin() as s:
            model = cls._get_model(s, model_id, filters)
            cls._call(s, pre_calls, data, model)
            for k, v in data.items():
                if hasattr(model, k):
                    setattr(model, k, v)
            s.flush()
            cls._call(s, post_calls, data, model)
            resource = cls._gen_resource_data(s, [model])[0]

        # Return response
        return response(message=cls.patch_message, data=resource)

    @classmethod
    def get(
        cls,
        model_id: int | None = None,
        filters: set[ColumnExpressionArgument[bool]] | None = None,
        post_calls: list[Callable] | None = None,
        as_list: bool = False,
        max_size: int | None = None,
        args_required: bool = False,
    ) -> Response:
        # Checks and parsing
        if cls.model is None:
            raise NotImplementedError
        if filters is None:
            filters = set()
        if post_calls is None:
            post_calls = []

        # Prepare data
        data = cls._gen_query_data(cls.get_args)
        if args_required and not data:
            abort(response(400, ApiText.HTTP_400))
        query_filters = cls._gen_query_filters(data)
        filters = filters.union(query_filters)

        # Get model
        with conn.begin() as s:
            if model_id is not None:
                models = [cls._get_model(s, model_id, filters)]
            else:
                limit = max_size or None
                models = s.query(cls.model).filter(*filters).limit(limit).all()
            cls._call(s, post_calls, data, models)
            resource = cls._gen_resource_data(s, models)

        # Return response
        if as_list:
            return response(message=cls.get_message, data=resource)
        return response(message=cls.get_message, data=resource[0])

    @classmethod
    def delete(
        cls,
        model_id: int,
        filters: set[ColumnExpressionArgument[bool]] | None = None,
        pre_calls: list[Callable] | None = None,
        post_calls: list[Callable] | None = None,
    ) -> Response:
        # Checks and parsing
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
            model = cls._get_model(s, model_id, filters)
            cls._call(s, pre_calls, None, model)
            s.delete(model)
            s.flush()
            cls._call(s, post_calls, None, None)

        # Return response
        return response(message=cls.delete_message)
