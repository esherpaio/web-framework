from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import Country, UserRoleLevel
from web.helper.user import access_control


class CountryAPI(API):
    model = Country
    post_attrs = {
        Country.code,
        Country.in_sitemap,
        Country.name,
        Country.currency_id,
        Country.region_id,
    }
    patch_attrs = {
        Country.code,
        Country.in_sitemap,
        Country.name,
        Country.currency_id,
        Country.region_id,
    }
    get_attrs = {
        Country.code,
        Country.in_sitemap,
        Country.name,
        Country.id,
        Country.currency_id,
        Country.region_id,
    }


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/countries")
def post_countries() -> Response:
    api = CountryAPI()
    return api.post()


@api_v1_bp.get("/countries")
def get_countries() -> Response:
    api = CountryAPI()
    return api.get(reference=None, as_list=True)


@api_v1_bp.get("/countries/<int:country_id>")
def get_countries_id(country_id: int) -> Response:
    api = CountryAPI()
    return api.get(country_id)


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/countries/<int:country_id>")
def delete_countries_id(country_id: int) -> Response:
    api = CountryAPI()
    return api.delete(country_id)
