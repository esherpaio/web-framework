from flask import Flask

from web.auth import Auth, jwt_login
from web.blueprint.admin import admin_bp
from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.robots import robots_bp
from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database import conn
from web.database.model import User, UserRoleId
from web.flask import FlaskWeb
from web.syncer import Syncer
from web.syncer.object import CountrySyncer, CurrencySyncer, RegionSyncer, SkuSyncer


class UserSyncer(Syncer):
    MODEL = User
    KEY = "api_key"
    SEEDS = [
        User(api_key="guest", is_active=True, role_id=UserRoleId.GUEST),
        User(api_key="user", is_active=True, role_id=UserRoleId.USER),
        User(api_key="external", is_active=True, role_id=UserRoleId.EXTERNAL),
        User(api_key="admin", is_active=True, role_id=UserRoleId.ADMIN),
        User(api_key="super", is_active=True, role_id=UserRoleId.SUPER),
    ]


def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule("/", endpoint="home", view_func=lambda: "Home")
    app.add_url_rule("/login", endpoint="login", view_func=view_login)
    FlaskWeb(
        app,
        blueprints=[robots_bp, admin_bp, api_v1_bp, webhook_v1_bp],
        accept_cookie_auth=True,
        accept_request_auth=True,
        syncers=[CurrencySyncer, RegionSyncer, CountrySyncer, SkuSyncer, UserSyncer],
    ).setup()
    Auth(app)
    return app


def view_login() -> str:
    with conn.begin() as s:
        user = s.query(User).filter(User.api_key == "admin").first()
    jwt_login(user.id)
    return "Logged in"
