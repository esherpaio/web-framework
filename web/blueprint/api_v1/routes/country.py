from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.client import conn
from web.database.model import Country, UserRoleLevel
from web.helper.api import response
from web.helper.user import access_control

#
# Configuration
#


class CountryAPI(API):
    model = Country
    post_columns = {
        Country.code,
        Country.in_sitemap,
        Country.name,
        Country.currency_id,
        Country.region_id,
    }
    get_columns = {
        Country.code,
        Country.in_sitemap,
        Country.name,
        Country.id,
        Country.currency_id,
        Country.region_id,
    }


#
# Endpoints
#


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/countries")
def post_countries() -> Response:
    api = CountryAPI()
    data = api.gen_request_data(api.post_columns)
    with conn.begin() as s:
        model = api.model()
        api.insert(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.get("/countries")
def get_countries() -> Response:
    api = CountryAPI()
    with conn.begin() as s:
        models = api.list_(s)
        resources = api.gen_resources(s, models)
    return response(data=resources)


@api_v1_bp.get("/countries/<int:country_id>")
def get_countries_id(country_id: int) -> Response:
    api = CountryAPI()
    with conn.begin() as s:
        model = api.get(s, country_id)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/countries/<int:country_id>")
def delete_countries_id(country_id: int) -> Response:
    api = CountryAPI()
    with conn.begin() as s:
        model = api.get(s, country_id)
        api.delete(s, model)
    return response()


#
# Functions
#
