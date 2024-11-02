from datetime import datetime, timezone

from sqlalchemy.orm import Session
from werkzeug import Response

from web.api import API, json_response
from web.app.blueprint import api_v1_bp
from web.auth import authorize
from web.database import conn
from web.database.model import AppSetting, UserRoleLevel

#
# Configuration
#


class SettingAPI(API):
    model = AppSetting
    patch_columns = {
        AppSetting.banner,
        AppSetting.cached_at,
    }
    get_columns = {
        AppSetting.banner,
        AppSetting.cached_at,
    }


#
# Endpoints
#


@api_v1_bp.get("/setting")
@authorize(UserRoleLevel.ADMIN)
def get_setting() -> Response:
    api = SettingAPI()
    with conn.begin() as s:
        model: AppSetting = api.get(s, None)
        resource = api.gen_resource(s, model)
    return json_response(data=resource)


@api_v1_bp.patch("/setting")
@authorize(UserRoleLevel.ADMIN)
def patch_setting() -> Response:
    api = SettingAPI()
    data = api.gen_data(api.patch_columns)
    with conn.begin() as s:
        model: AppSetting = api.get(s, None)
        set_cache(s, data, model)
        api.update(s, data, model)
        resource = api.gen_resource(s, model)
    return json_response(data=resource)


#
# Functions
#


def set_cache(s: Session, data: dict, model: AppSetting) -> None:
    if "cached_at" in data:
        data["cached_at"] = datetime.now(timezone.utc).isoformat()
