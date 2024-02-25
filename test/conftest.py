import contextlib

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn, engine
from web.database.model import Base, User, UserRoleId
from web.flask import FlaskWeb
from web.seeder.seed import (
    FileTypeSyncer,
    OrderStatusSyncer,
    ProductLinkeTypeSyncer,
    ProductTypeSyncer,
    UserRoleSyncer,
)

#
# Pytest configuration
#

pytest_plugins = [
    "test.fixtures.models",
]


def pytest_configure(*args) -> None:
    drop_tables()


def drop_tables() -> None:
    meta = Base.metadata
    with contextlib.closing(engine.connect()) as conn:
        trans = conn.begin()
        for table in reversed(meta.sorted_tables):
            conn.execute(table.delete())
        trans.commit()


#
# Flask setup
#


def create_app() -> Flask:
    app = Flask(__name__)
    app.testing = True
    web = FlaskWeb(
        app,
        blueprints=[api_v1_bp, webhook_v1_bp],
        accept_cookie_auth=True,
        accept_request_auth=True,
        db_hook=db_hook,
    )
    web.setup()
    web.stop_cache()
    app.config["web"] = web
    return app


def db_hook(*args) -> None:
    with conn.begin() as s:
        FileTypeSyncer().sync(s)
        OrderStatusSyncer().sync(s)
        ProductLinkeTypeSyncer().sync(s)
        ProductTypeSyncer().sync(s)
        UserRoleSyncer().sync(s)
        create_users(s)


@pytest.fixture(scope="module", autouse=True)
def update_cache(app) -> None:
    web = app.config["web"]
    web.update_cache(force=True)


@pytest.fixture(scope="session")
def app() -> Flask:
    return create_app()


@pytest.fixture(scope="session")
def client(app) -> FlaskClient:
    return app.test_client()


#
# User objects
#

user_data = [
    {
        "api_key": "guest",
        "email": "guest@enlarge-online.nl",
        "role_id": UserRoleId.GUEST,
        "is_active": True,
    },
    {
        "api_key": "user",
        "email": "user@enlarge-online.nl",
        "role_id": UserRoleId.USER,
        "is_active": True,
    },
    {
        "api_key": "admin",
        "email": "admin@enlarge-online.nl",
        "role_id": UserRoleId.ADMIN,
        "is_active": True,
    },
]


def create_users(s: Session) -> None:
    for data in user_data:
        user = s.query(User).filter_by(**data).first()
        if user is None:
            user = User(**data)
            s.add(user)
            s.flush()


@pytest.fixture(scope="session")
def guest() -> dict[str, str]:
    return {"Authorization": "Bearer guest"}


@pytest.fixture(scope="session")
def user() -> dict[str, str]:
    return {"Authorization": "Bearer user"}


@pytest.fixture(scope="session")
def admin() -> dict[str, str]:
    return {"Authorization": "Bearer admin"}
