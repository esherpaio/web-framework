from datetime import datetime

from sqlalchemy.orm import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.client import conn
from web.database.model import AppSetting, UserRoleLevel
from web.helper.api import response
from web.helper.user import access_control

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
@access_control(UserRoleLevel.ADMIN)
def get_setting() -> Response:
    api = SettingAPI()
    with conn.begin() as s:
        model: AppSetting = api.get(s, None)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.patch("/setting")
@access_control(UserRoleLevel.ADMIN)
def patch_setting() -> Response:
    api = SettingAPI()
    data = api.gen_request_data(api.patch_columns)
    with conn.begin() as s:
        model: AppSetting = api.get(s, None)
        set_cache(s, data, model)
        api.update(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


#
# Functions
#


def set_cache(s: Session, data: dict, model: AppSetting) -> None:
    if "cached_at" in data:
        data["cached_at"] = datetime.utcnow().isoformat()
