from flask import Flask

from web.app.blueprint.admin_v1 import (
    admin_v1_bp,
    admin_v1_css_bundle,
    admin_v1_js_bundle,
)
from web.app.blueprint.api_v1 import api_v1_bp
from web.app.blueprint.auth_v1 import auth_v1_bp
from web.app.blueprint.robots_v1 import robots_v1_bp
from web.app.blueprint.webhook_v1 import webhook_v1_bp
from web.app.flask import FlaskWeb
from web.auth import jwt_login
from web.automation import Syncer
from web.automation.task import (
    CountrySyncer,
    CurrencySyncer,
    RegionSyncer,
    SkuSyncer,
    StaticSeed,
    StaticType,
)
from web.automation.task import StaticSyncer as _StaticSyncer
from web.database import conn
from web.database.model import AppSetting, User, UserRoleId


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


class StaticSyncer(_StaticSyncer):
    SEEDS = [
        StaticSeed(
            type_=StaticType.JS,
            bundles=[admin_v1_js_bundle],
            model=AppSetting,
        ),
        StaticSeed(
            type_=StaticType.CSS,
            bundles=[admin_v1_css_bundle],
            model=AppSetting,
        ),
    ]


def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule("/", endpoint="home", view_func=lambda: "Home")
    app.add_url_rule("/fnorce-login", endpoint="login", view_func=view_force_login)
    FlaskWeb(
        app,
        blueprints=[
            api_v1_bp,
            auth_v1_bp,
            webhook_v1_bp,
            robots_v1_bp,
            admin_v1_bp,
        ],
        auto_tasks=[
            CurrencySyncer,
            RegionSyncer,
            CountrySyncer,
            SkuSyncer,
            UserSyncer,
            StaticSyncer,
        ],
    )
    return app


def view_force_login() -> str:
    with conn.begin() as s:
        user = s.query(User).filter(User.api_key == "admin").first()
    jwt_login(user.id)
    return "Logged in"
