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
    }
    get_columns = {
        Setting.banner,
    }


#
# Endpoints
#


@api_v1_bp.get("/setting")
def get_billings_id(billing_id: int) -> Response:
    api = SettingAPI()
    with conn.begin() as s:
        model = api.get(s, billing_id)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.patch("/setting")
def patch_billings_id(billing_id: int) -> Response:
    api = SettingAPI()
    data = api.gen_request_data(api.patch_columns)
    with conn.begin() as s:
        model = api.get(s, billing_id)
        api.update(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


#
# Functions
#
