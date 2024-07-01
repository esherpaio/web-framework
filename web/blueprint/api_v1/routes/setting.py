from datetime import datetime

from sqlalchemy.orm import Session
from werkzeug import Response

from web.api import API
from web.api.utils import json_response
from web.blueprint.api_v1 import api_v1_bp
from web.database import conn
from web.database.model import AppSetting, UserRoleLevel
from web.security import secure

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
@secure(UserRoleLevel.ADMIN)
def get_setting() -> Response:
    api = SettingAPI()
    with conn.begin() as s:
        model: AppSetting = api.get(s, None)
        resource = api.gen_resource(s, model)
    return json_response(data=resource)


@api_v1_bp.patch("/setting")
@secure(UserRoleLevel.ADMIN)
def patch_setting() -> Response:
    api = SettingAPI()
    data = api.gen_request_data(api.patch_columns)
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
        data["cached_at"] = datetime.utcnow().isoformat()
