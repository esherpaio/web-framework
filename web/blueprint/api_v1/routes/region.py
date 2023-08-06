from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.client import conn
from web.database.model import Region, UserRoleLevel
from web.helper.api import response
from web.helper.user import access_control

#
# Configuration
#


class RegionAPI(API):
    model = Region
    post_columns = {
        Region.name,
    }
    get_columns = {
        Region.name,
        Region.id,
    }


#
# Endpoints
#


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/regions")
def post_regions() -> Response:
    api = RegionAPI()
    data = api.gen_request_data(api.post_columns)
    with conn.begin() as s:
        model = api.model()
        api.insert(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.get("/regions")
def get_regions() -> Response:
    api = RegionAPI()
    with conn.begin() as s:
        models = api.list_(s)
        resources = api.gen_resources(s, models)
    return response(data=resources)


@api_v1_bp.get("/regions/<int:region_id>")
def get_regions_id(region_id: int) -> Response:
    api = RegionAPI()
    with conn.begin() as s:
        model = api.get(s, region_id)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/regions/<int:region_id>")
def delete_regions_id(region_id: int) -> Response:
    api = RegionAPI()
    with conn.begin() as s:
        model = api.get(s, region_id)
        api.delete(s, model)
    return response()


#
# Functions
#
