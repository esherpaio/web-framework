from typing import Any, Callable, Type

from flask import abort
from sqlalchemy import Column, ColumnExpressionArgument
from werkzeug import Response

from web.database.client import conn
from web.database.model import Base, Model
from web.helper.api import ApiText, json_get, response


class API:
    model: Type[Base] | None = None
    post_attrs: set[Column] = set()
    post_callbacks: list[Callable] = []
    patch_attrs: set[Column] = set()
    patch_callbacks: list[Callable] = []
    get_attrs: set[Column] = set()
    get_callbacks: list[Callable] = []

    #
    # Functions
    #

    @staticmethod
    def _gen_request_data(
        attrs: set[Column],
    ) -> dict[str, Any]:
        data = {}
        for attr in attrs:
            value, _ = json_get(
                attr.name,
                attr.type.python_type,
                nullable=bool(attr.nullable),
                default=attr.default,
            )
            data[attr.name] = value
        return data

    @staticmethod
    def _get_query_results(
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> list[Model | None]:
        results = []
        with conn.begin() as s:
            for model, conditions in queries.items():
                result = s.query(model).filter(*conditions).first()
                results.append(result)
        return results

    #
    # Authorization
    #

    @classmethod
    def raise_all_is_none(
        cls,
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> None:
        """Check if all of the queries return None."""
        results = cls._get_query_results(queries)
        if all(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_all_is_not_none(
        cls,
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> None:
        """Check if all of the queries return not None."""
        results = cls._get_query_results(queries)
        if all(x is not None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_any_is_none(
        cls,
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> None:
        """Check if any of the queries return None."""
        results = cls._get_query_results(queries)
        if any(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    @classmethod
    def raise_any_is_not_none(
        cls,
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
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
        include_request: bool = True,
        add_data: dict | None = None,
    ) -> Response:
        """Post a resource from `post_attrs`."""

        if cls.model is None:
            raise NotImplementedError

        # Generate data
        data: dict = {}
        if include_request:
            request_data = cls._gen_request_data(cls.post_attrs)
            data.update(**request_data)
        if add_data is not None:
            data.update(add_data)

        # Insert model
        with conn.begin() as s:
            model = cls.model(**data)
            s.add(model)
        return cls.get(model)

    @classmethod
    def patch(
        cls,
        model_id: int,
        include_request: bool = True,
        add_data: dict | None = None,
        conditions: tuple[ColumnExpressionArgument[bool], ...] | None = None,
    ) -> Response:
        """Patch a resource from `patch_attrs`."""

        if cls.model is None:
            raise NotImplementedError

        # Generate data
        data: dict = {}
        if include_request:
            request_data = cls._gen_request_data(cls.post_attrs)
            data.update(**request_data)
        if add_data is not None:
            data.update(add_data)

        # Get model
        if conditions is None:
            conditions = ()
        with conn.begin() as s:
            model = (
                s.query(cls.model).filter(cls.model.id == model_id, *conditions).first()
            )

            # Check if model exists
            if not model:
                abort(response(404, ApiText.HTTP_404))

            # Update model from data
            for k, v in data.items():
                if hasattr(model, k):
                    setattr(model, k, v)
            s.flush()

            # Run callbacks
            for callback in cls.patch_callbacks:
                callback(s, model)

        return cls.get(model)

    @classmethod
    def get(
        cls,
        reference: Type[Base] | int,
        conditions: tuple[ColumnExpressionArgument[bool], ...] | None = None,
    ) -> Response:
        """Get a resource from `get_attrs`."""

        if cls.model is None:
            raise NotImplementedError

        # Parse reference to model
        if isinstance(reference, int):
            if conditions is None:
                conditions = ()
            with conn.begin() as s:
                model = (
                    s.query(cls.model)
                    .filter(cls.model.id == reference, *conditions)
                    .first()
                )
        elif isinstance(reference, Model):
            model = reference

        # Check if model exists
        if not model:
            abort(response(404, ApiText.HTTP_404))

        # Generate data
        data = {}
        for attr in cls.get_attrs:
            data[attr.name] = getattr(model, attr.name)

        # Create response
        return response(data=data)
