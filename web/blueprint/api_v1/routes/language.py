from werkzeug import Response

from web.api import API
from web.api.utils import response
from web.blueprint.api_v1 import api_v1_bp
from web.database import conn
from web.database.model import Language, UserRoleLevel
from web.libs.auth import access_control

#
# Configuration
#


class LanguageAPI(API):
    model = Language
    post_columns = {
        Language.code,
        Language.in_sitemap,
        Language.name,
    }
    get_columns = {
        Language.code,
        Language.in_sitemap,
        Language.name,
    }


#
# Endpoints
#


@api_v1_bp.post("/languages")
@access_control(UserRoleLevel.ADMIN)
def post_languages() -> Response:
    api = LanguageAPI()
    data = api.gen_request_data(api.post_columns)
    with conn.begin() as s:
        model = api.model()
        api.insert(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.get("/languages")
def get_languages() -> Response:
    api = LanguageAPI()
    with conn.begin() as s:
        models: list[Language] = api.list_(s)
        resources = api.gen_resources(s, models)
    return response(data=resources)


@api_v1_bp.get("/languages/<int:language_id>")
def get_languages_id(language_id: int) -> Response:
    api = LanguageAPI()
    with conn.begin() as s:
        model: Language = api.get(s, language_id)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.delete("/languages/<int:language_id>")
@access_control(UserRoleLevel.ADMIN)
def delete_languages_id(language_id: int) -> Response:
    api = LanguageAPI()
    with conn.begin() as s:
        model: Language = api.get(s, language_id)
        api.delete(s, model)
    return response()


#
# Functions
#
