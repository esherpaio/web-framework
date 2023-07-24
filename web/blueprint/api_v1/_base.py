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

    post_attrs: set[Column] = set()
    post_callbacks: list[Callable] = []
    patch_attrs: set[Column] = set()
    patch_callbacks: list[Callable] = []
    get_args: set[Column] = set()
    get_attrs: set[Column] = set()
    get_callbacks: list[Callable] = []
    delete_callbacks: list[Callable] = []

    #
    # Functions
    #

    @staticmethod
    def _gen_request_data(
        attrs: set[Column],
    ) -> dict[str, Any]:
        if not has_request_context():
            raise RuntimeError
        if request.json is None:
            return {}

        request_json = request.json
        data = {}
        for attr in attrs:
            if attr.name not in request_json:
                continue
            value, _ = json_get(
                attr.name,
                attr.type.python_type,
                nullable=bool(attr.nullable),
                default=attr.default,
            )
            data[attr.name] = value
        return data

    @classmethod
    def _gen_query_conditions(
        cls,
        attrs: set[Column],
    ) -> set[ColumnExpressionArgument[bool]]:
        if not has_request_context():
            raise RuntimeError
        if request.args is None:
            return set()

        request_args = request.args.to_dict()
        data = set()
        for attr in attrs:
            if attr.name not in request_args:
                continue
            if not hasattr(cls.model, attr.name):
                continue
            value, _ = args_get(
                attr.name,
                attr.type.python_type,
                nullable=bool(attr.nullable),
                default=attr.default,
            )
            cond = getattr(cls.model, attr.name) == value
            data.add(cond)
        return data

    @staticmethod
    def _get_query_results(
        queries: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> list[Model | None]:
        results = []
        with conn.begin() as s:
            for model, conditions in queries.items():
                result = s.query(model).filter(*conditions).first()
                results.append(result)
        return results

    @classmethod
    def _call_callbacks(
        cls,
        s: Session,
        model: Type[Model] | None,
        callbacks: list[Callable],
    ) -> None:
        for callback in callbacks:
            callback(s, model)
            s.flush()

    #
    # Authorization
    #

    @classmethod
    def raise_all_is_none(
        cls,
        queries: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if all of the queries return None."""
        results = cls._get_query_results(queries)
        if all(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_all_is_not_none(
        cls,
        queries: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if all of the queries return not None."""
        results = cls._get_query_results(queries)
        if all(x is not None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_any_is_none(
        cls,
        queries: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if any of the queries return None."""
        results = cls._get_query_results(queries)
        if any(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_any_is_not_none(
        cls,
        queries: dict[type[Model], set[ColumnExpressionArgument[bool]]],
    ) -> None:
        """Check if any of the queries return not None."""
        results = cls._get_query_results(queries)
        if any(x is not None for x in results):
            abort(response(403, ApiText.HTTP_403))

    #
    # Operations
    #

    @classmethod
    def post(
        cls,
        add_data: dict | None = None,
    ) -> Response:
        # Sanity checks
        if cls.model is None:
            raise NotImplementedError

        # Generate data
        data = cls._gen_request_data(cls.post_attrs)
        if add_data is not None:
            data.update(add_data)

        # Insert model
        with conn.begin() as s:
            model = cls.model(**data)
            s.add(model)
            cls._call_callbacks(s, model, cls.post_callbacks)

        return cls.get(model)

    @classmethod
    def get(
        cls,
        reference: Type[Model] | int | None = None,
        conditions: set[ColumnExpressionArgument[bool]] | None = None,
        as_list: bool = False,
    ) -> Response:
        # Sanity checks
        if cls.model is None:
            raise NotImplementedError
        if conditions is None:
            conditions = set()

        # Generate query
        query_conditions = cls._gen_query_conditions(cls.get_args)
        conditions = conditions.union(query_conditions)

        # Parse reference to models
        with conn.begin() as s:
            if reference is None:
                models = s.query(cls.model).filter(*conditions).all()
            elif isinstance(reference, int):
                models = [
                    (
                        s.query(cls.model)
                        .filter(cls.model.id == reference, *conditions)
                        .first()
                    )
                ]
            elif isinstance(reference, Model):
                models = [reference]
            for model in models:
                cls._call_callbacks(s, model, cls.get_callbacks)

        # Check if model exists
        if not models and not as_list:
            abort(response(404, ApiText.HTTP_404))

        # Generate data
        data = []
        for model in models:
            model_data = {}
            for attr in cls.get_attrs:
                model_data[attr.name] = getattr(model, attr.name)
            data.append(model_data)

        # Create response
        if as_list:
            return response(data=data)
        else:
            return response(data=data[0])

    @classmethod
    def patch(
        cls,
        model_id: int,
        add_data: dict | None = None,
        conditions: set[ColumnExpressionArgument[bool]] | None = None,
    ) -> Response:
        # Sanity checks
        if cls.model is None:
            raise NotImplementedError
        if conditions is None:
            conditions = set()

        # Generate data
        data = cls._gen_request_data(cls.post_attrs)
        if add_data is not None:
            data.update(add_data)

        # Patch model
        with conn.begin() as s:
            model = (
                s.query(cls.model).filter(cls.model.id == model_id, *conditions).first()
            )
            if model is None:
                abort(response(404, ApiText.HTTP_404))
            for k, v in data.items():
                if hasattr(model, k):
                    setattr(model, k, v)
            s.flush()
            cls._call_callbacks(s, model, cls.patch_callbacks)

        return cls.get(model)

    @classmethod
    def delete(
        cls,
        model_id: int,
        conditions: set[ColumnExpressionArgument[bool]] | None = None,
    ) -> Response:
        # Sanity checks
        if cls.model is None:
            raise NotImplementedError
        if conditions is None:
            conditions = set()

        # Delete model
        with conn.begin() as s:
            model = (
                s.query(cls.model).filter(cls.model.id == model_id, *conditions).first()
            )
            if model is None:
                abort(response(404, ApiText.HTTP_404))
            s.delete(model)
            cls._call_callbacks(s, model, cls.delete_callbacks)

        return response()
