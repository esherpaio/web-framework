from datetime import datetime

from sqlalchemy.orm import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.client import conn
from web.database.model import Setting
from web.helper.api import response

#
# Configuration
#


class SettingAPI(API):
    model = Setting
    patch_columns = {
        Setting.banner,
        Setting.cached_at,
    }
    get_columns = {
        Setting.banner,
        Setting.cached_at,
    }


#
# Endpoints
#


@api_v1_bp.get("/setting")
def get_setting() -> Response:
    api = SettingAPI()
    with conn.begin() as s:
        model = api.get(s, None)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.patch("/setting")
def patch_setting() -> Response:
    api = SettingAPI()
    data = api.gen_request_data(api.patch_columns)
    with conn.begin() as s:
        model = api.get(s, None)
        set_cache(s, data, model)
        api.update(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


#
# Functions
#


def set_cache(s: Session, data: dict, model: Setting) -> None:
    if "cached_at" in data:
        data["cached_at"] = datetime.utcnow().isoformat()
