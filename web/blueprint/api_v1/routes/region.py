from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import Region, UserRoleLevel
from web.helper.user import access_control


class RegionAPI(API):
    model = Region
    post_attrs = {Region.name}
    patch_attrs = {Region.name}
    get_attrs = {Region.name, Region.id}


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/regions")
def post_regions() -> Response:
    api = RegionAPI()
    return api.post()


@api_v1_bp.get("/regions")
def get_regions() -> Response:
    api = RegionAPI()
    return api.get(as_list=True)


@api_v1_bp.get("/regions/<int:region_id>")
def get_regions_id(region_id: int) -> Response:
    api = RegionAPI()
    return api.get(region_id)


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/regions/<int:region_id>")
def delete_regions_id(region_id: int) -> Response:
    api = RegionAPI()
    return api.delete(region_id)
