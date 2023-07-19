from typing import Type

from flask import abort
from sqlalchemy import Column, ColumnExpressionArgument

from web.database.client import conn
from web.database.model import Model
from web.helper.api import ApiText, json_get, response


class API:
    model: Type[Model] | None = None
    post_attrs: set[Column] = set()
    post_callbacks: list[callable] = []
    patch_attrs: set[Column] = set()
    patch_callbacks: list[callable] = []
    get_attrs: set[Column] = set()
    get_callbacks: list[callable] = []

    #
    # Functions
    #

    @staticmethod
    def _gen_request_data(
        attrs: set[Column],
    ) -> dict[str, any]:
        data = {}
        for attr in attrs:
            value, _ = json_get(
                attr.name,
                attr.type.python_type,
                nullable=attr.nullable,
                default=attr.default,
            )
            data[attr.name] = value
        return data

    @staticmethod
    def _get_query_results(
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> list[Type[Model]]:
        results = []
        with conn.begin() as s:
            for model, conditions in queries.items():
                result = s.query(model).filter(*conditions).first()
                results.append(result)
        return results

    #
    # Authorization
    #

    def raise_all_is_none(
        self,
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> None:
        """Check if all of the queries return None."""
        results = self._get_query_results(queries)
        if all(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    def raise_all_is_not_none(
        self,
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> None:
        """Check if all of the queries return not None."""
        results = self._get_query_results(queries)
        if all(x is not None for x in results):
            abort(response(403, ApiText.HTTP_403))

    def raise_any_is_none(
        self,
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> None:
        """Check if any of the queries return None."""
        results = self._get_query_results(queries)
        if any(x is None for x in results):
            abort(response(403, ApiText.HTTP_403))

    def raise_any_is_not_none(
        self,
        queries: dict[type[Model], tuple[ColumnExpressionArgument[bool], ...]],
    ) -> None:
        """Check if any of the queries return not None."""
        results = self._get_query_results(queries)
        if any(x is not None for x in results):
            abort(response(403, ApiText.HTTP_403))

    #
    # Operations
    #

    def post(
        self,
        include_request: bool = True,
        add_data: dict | None = None,
    ) -> Type[Model]:
        """Post a resource from `post_attrs`."""

        # Generate data
        data = {}
        if include_request:
            request_data = self._gen_request_data(self.post_attrs)
            data.update(**request_data)
        if add_data is not None:
            data.update(add_data)

        # Insert model
        with conn.begin() as s:
            model = self.model(**data)
            s.add(model)
        return self.get(model)

    def patch(
        self,
        model_id: int,
        include_request: bool = True,
        add_data: dict | None = None,
        conditions: tuple[ColumnExpressionArgument[bool], ...] | None = None,
    ) -> Type[Model]:
        """Patch a resource from `patch_attrs`."""

        # Generate data
        data = {}
        if include_request:
            request_data = self._gen_request_data(self.post_attrs)
            data.update(**request_data)
        if add_data is not None:
            data.update(add_data)

        # Get model
        if conditions is None:
            conditions = ()
        with conn.begin() as s:
            model = (
                s.query(self.model)
                .filter(self.model.id == model_id, *conditions)
                .first()
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
            for callback in self.patch_callbacks:
                callback(s, model)

        return self.get(model)

    def get(
        self,
        reference: Type[Model] | int,
        conditions: tuple[ColumnExpressionArgument[bool], ...] | None = None,
    ) -> dict:
        """Get a resource from `get_attrs`."""

        # Parse reference to model
        if isinstance(reference, int):
            if conditions is None:
                conditions = ()
            with conn.begin() as s:
                model = (
                    s.query(self.model)
                    .filter(self.model.id == reference, *conditions)
                    .first()
                )
        elif isinstance(reference, Model):
            model = reference

        # Check if model exists
        if not model:
            abort(response(404, ApiText.HTTP_404))

        # Generate data
        data = {}
        for attr in self.get_attrs:
            data[attr.name] = getattr(model, attr.name)

        # Create response
        return response(data=data)
