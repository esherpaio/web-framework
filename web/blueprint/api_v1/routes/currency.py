from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import Currency, UserRoleLevel
from web.helper.user import access_control


class CurrencyAPI(API):
    model = Currency
    post_attrs = {Currency.code, Currency.rate, Currency.symbol}
    patch_attrs = {Currency.code, Currency.rate, Currency.symbol}
    get_attrs = {Currency.code, Currency.rate, Currency.symbol, Currency.id}


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/currencies")
def post_currencies() -> Response:
    api = CurrencyAPI()
    return api.post()


@api_v1_bp.get("/currencies")
def get_currencies() -> Response:
    api = CurrencyAPI()
    return api.get(reference=None, as_list=True)


@api_v1_bp.get("/currencies/<int:currency_id>")
def get_currencies_id(currency_id: int) -> Response:
    api = CurrencyAPI()
    return api.get(currency_id)


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/currencies/<int:currency_id>")
def delete_currencies_id(currency_id: int) -> Response:
    api = CurrencyAPI()
    return api.delete(currency_id)
