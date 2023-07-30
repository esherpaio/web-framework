import base64
import contextlib
from typing import Generator

import alembic.config
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_login import LoginManager
from werkzeug import Response

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn, engine
from web.database.model import (
    Base,
    Country,
    Currency,
    Language,
    Region,
    User,
    UserRoleId,
)
from web.helper.cache import cache
from web.helper.user import load_request, load_user
from web.seeder.model import (
    FileTypeSyncer,
    OrderStatusSyncer,
    ProductLinkeTypeSyncer,
    ProductTypeSyncer,
    UserRoleSyncer,
)

# Static


pytest_plugins = [
    "tests.fixtures.models",
]
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


# Configuration


def pytest_configure(*args) -> None:
    alembic.config.main(argv=["upgrade", "head"])
    drop_tables()
    run_seeders()
    create_users()


def drop_tables() -> None:
    meta = Base.metadata
    with contextlib.closing(engine.connect()) as conn:
        trans = conn.begin()
        for table in reversed(meta.sorted_tables):
            conn.execute(table.delete())
        trans.commit()


def run_seeders() -> None:
    with conn.begin() as s:
        FileTypeSyncer().sync(s)
        OrderStatusSyncer().sync(s)
        ProductLinkeTypeSyncer().sync(s)
        ProductTypeSyncer().sync(s)
        UserRoleSyncer().sync(s)


def create_users() -> None:
    with conn.begin() as s:
        for data in user_data:
            user = s.query(User).filter_by(**data).first()
            if user is None:
                user = User(**data)
                s.add(user)
                s.flush()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["DEBUG"] = config.APP_DEBUG
    app.config["SECRET_KEY"] = config.APP_SECRET
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(webhook_v1_bp)
    login_manager = LoginManager(app)
    login_manager.session_protection = "strong"
    login_manager.login_view = config.ENDPOINT_LOGIN
    login_manager.user_loader(load_user)
    login_manager.request_loader(load_request)
    app.add_url_rule("/login", endpoint=config.ENDPOINT_LOGIN, view_func=url_response)
    return app


def url_response(*args, **kwargs) -> Response:
    return Response(status=200)


@pytest.fixture(scope="module", autouse=True)
def update_cache() -> None:
    with conn.begin() as s:
        cache.countries = s.query(Country).order_by(Country.name).all()
        cache.currencies = s.query(Currency).order_by(Currency.code).all()
        cache.languages = s.query(Language).order_by(Language.code).all()
        cache.regions = s.query(Region).order_by(Region.name).all()


# Flask app


@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    app = create_app()
    yield app


@pytest.fixture(scope="session")
def client(app) -> FlaskClient:
    return app.test_client()


# Authorization headers


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
