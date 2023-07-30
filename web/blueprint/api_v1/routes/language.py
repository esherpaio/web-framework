from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import Language, UserRoleLevel
from web.helper.user import access_control


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


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/languages")
def post_languages() -> Response:
    api = LanguageAPI()
    return api.post()


@api_v1_bp.get("/languages")
def get_languages() -> Response:
    api = LanguageAPI()
    return api.get(reference=None, as_list=True)


@api_v1_bp.get("/languages/<int:language_id>")
def get_languages_id(language_id: int) -> Response:
    api = LanguageAPI()
    return api.get(language_id)


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/languages/<int:language_id>")
def delete_languages_id(language_id: int) -> Response:
    api = LanguageAPI()
    return api.delete(language_id)
