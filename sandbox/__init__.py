import flask_login
from flask import Flask
from werkzeug.security import generate_password_hash

import web.seeder.model as seed
from web.base import FlaskWeb
from web.blueprint.admin import admin_bp
from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn
from web.database.model import Category
from web.database.model.user import User
from web.database.model.user_role import UserRoleId


def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule("/", endpoint="home", view_func=view_home)
    app.add_url_rule("/login", endpoint="login", view_func=view_login)
    FlaskWeb(
        app,
        accept_cookie_auth=True,
        accept_request_auth=True,
        blueprints=[admin_bp, api_v1_bp, webhook_v1_bp],
        enable_locale=True,
        enable_packer=True,
        seed_hook=seed_hook,
    ).setup()
    return app


def seed_hook(*args) -> None:
    with conn.begin() as s:
        # defaults
        seed.FileTypeSyncer().sync(s)
        seed.OrderStatusSyncer().sync(s)
        seed.ProductLinkeTypeSyncer().sync(s)
        seed.ProductTypeSyncer().sync(s)
        seed.UserRoleSyncer().sync(s)
        # third party
        seed.CurrencySyncer().sync(s)
        seed.RegionSyncer().sync(s)
        seed.CountrySyncer().sync(s)
        # user defined
        seed.SkuSyncer().sync(s)


def view_home() -> str:
    return "Hello, World!"


def view_login() -> str:
    admin_email = "admin@localhost.com"
    password_hash = generate_password_hash("admin", "pbkdf2:sha256:1000000")
    with conn.begin() as s:
        user = s.query(User).filter(User.email == admin_email).first()
        if not user:
            user = User(
                email=admin_email,
                is_active=True,
                password_hash=password_hash,
                role_id=UserRoleId.ADMIN,
            )
            s.add(user)
        flask_login.logout_user()
        flask_login.login_user(user, remember=True)
    return "Logged in as admin"
