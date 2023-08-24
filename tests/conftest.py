import base64
import contextlib

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from web.base import FlaskWeb
from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn, engine
from web.database.model import Base, User, UserRoleId
from web.seeder.model import (
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
    "tests.fixtures.models",
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
        seed_hook=seed_hook,
        enable_localization=True,
    )
    web.setup()
    app.web = web  # type: ignore
    return app


def seed_hook(*args) -> None:
    with conn.begin() as s:
        FileTypeSyncer().sync(s)
        OrderStatusSyncer().sync(s)
        ProductLinkeTypeSyncer().sync(s)
        ProductTypeSyncer().sync(s)
        UserRoleSyncer().sync(s)
        create_users(s)


@pytest.fixture(scope="module", autouse=True)
def update_cache(app) -> None:
    app.web.update_cache()


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
    },
    {
        "api_key": "user",
        "email": "user@enlarge-online.nl",
        "role_id": UserRoleId.USER,
    },
    {
        "api_key": "admin",
        "email": "admin@enlarge-online.nl",
        "role_id": UserRoleId.ADMIN,
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
    credentials = base64.b64encode(b"guest").decode()
    return {"Authorization": f"Basic {credentials}"}


@pytest.fixture(scope="session")
def user() -> dict[str, str]:
    credentials = base64.b64encode(b"user").decode()
    return {"Authorization": f"Basic {credentials}"}


@pytest.fixture(scope="session")
def admin() -> dict[str, str]:
    credentials = base64.b64encode(b"admin").decode()
    return {"Authorization": f"Basic {credentials}"}
