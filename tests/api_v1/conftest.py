import base64
from typing import Generator

import alembic.config
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_login import LoginManager

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn
from web.database.model import User, UserRoleId
from web.helper.user import load_request, load_user
from web.seeder.utils import run_seeders


def pytest_configure(*args) -> None:
    # todo: external seeds do not work in GitHub Actions,
    #  instead we should create API endpoints
    #  and run those tests first so we can use that data in other tests
    config.SEED_EXTERNAL = False
    alembic.config.main(argv=["upgrade", "head"])
    run_seeders()
    create_users()


def create_users() -> None:
    user_data = [
        {"api_key": "guest", "role_id": UserRoleId.GUEST},
        {"api_key": "user", "role_id": UserRoleId.USER},
        {"api_key": "admin", "role_id": UserRoleId.ADMIN},
    ]
    with conn.begin() as s:
        for data in user_data:
            user = s.query(User).filter_by(**data).first()
            if user is None:
                user = User(**data)
                s.add(user)


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
    return app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    app = create_app()
    yield app


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope="session")
def guest_headers() -> dict[str, str]:
    credentials = base64.b64encode(b"guest").decode()
    return {"Authorization": f"Basic {credentials}"}


@pytest.fixture(scope="session")
def user_headers() -> dict[str, str]:
    credentials = base64.b64encode(b"user").decode()
    return {"Authorization": f"Basic {credentials}"}


@pytest.fixture(scope="session")
def admin_headers() -> dict[str, str]:
    credentials = base64.b64encode(b"admin").decode()
    return {"Authorization": f"Basic {credentials}"}
