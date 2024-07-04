import contextlib

import pytest
from flask import Flask
from flask.testing import FlaskClient

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.webhook_v1 import webhook_v1_bp
from web.cache import cache_manager
from web.database.client import engine
from web.database.model import Base, User, UserRoleId
from web.flask import FlaskWeb
from web.syncer import Syncer

#
# Configuration
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
# Syncers
#


class UserSyncer(Syncer):
    MODEL = User
    KEY = "api_key"
    SEEDS = [
        User(
            api_key="guest",
            email="guest@enlarge-online.nl",
            is_active=True,
            role_id=UserRoleId.GUEST,
        ),
        User(
            api_key="user",
            email="user@enlarge-online.nl",
            is_active=True,
            role_id=UserRoleId.USER,
        ),
        User(
            api_key="admin",
            email="admin@enlarge-online.nl",
            is_active=True,
            role_id=UserRoleId.ADMIN,
        ),
    ]


#
# Flask
#


def create_app() -> Flask:
    app = Flask(__name__)
    app.testing = True
    web = FlaskWeb(
        app,
        blueprints=[api_v1_bp, webhook_v1_bp],
        accept_cookie_auth=True,
        accept_request_auth=True,
        syncers=[UserSyncer],
    )
    web.setup()
    cache_manager._active = False
    app.config["web"] = web
    return app


@pytest.fixture(scope="module", autouse=True)
def update_cache() -> None:
    cache_manager.update(force=True)


@pytest.fixture(scope="session")
def app() -> Flask:
    return create_app()


@pytest.fixture(scope="session")
def client(app) -> FlaskClient:
    return app.test_client()


#
# Authentication
#


@pytest.fixture(scope="session")
def guest() -> dict[str, str]:
    return {"Authorization": "Bearer guest"}


@pytest.fixture(scope="session")
def user() -> dict[str, str]:
    return {"Authorization": "Bearer user"}


@pytest.fixture(scope="session")
def admin() -> dict[str, str]:
    return {"Authorization": "Bearer admin"}
