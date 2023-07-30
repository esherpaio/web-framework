from flask_login import current_user
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import Billing, Cart, Order
from web.helper.cart import get_vat


class BillingAPI(API):
    model = Billing
    post_columns = {
        Billing.address,
        Billing.city,
        Billing.company,
        Billing.country_id,
        Billing.email,
        Billing.first_name,
        Billing.last_name,
        Billing.phone,
        Billing.vat,
        Billing.zip_code,
    }
    patch_columns = {
        Billing.address,
        Billing.city,
        Billing.company,
        Billing.country_id,
        Billing.email,
        Billing.first_name,
        Billing.last_name,
        Billing.phone,
        Billing.vat,
        Billing.zip_code,
    }
    get_columns = {
        Billing.address,
        Billing.city,
        Billing.company,
        Billing.country_id,
        Billing.email,
        Billing.first_name,
        Billing.id,
        Billing.last_name,
        Billing.phone,
        Billing.user_id,
        Billing.vat,
        Billing.zip_code,
    }


@api_v1_bp.post("/billings")
def post_billings() -> Response:
    api = BillingAPI()
    return api.post(add_request={"user_id": current_user.id})


@api_v1_bp.get("/billings/<int:billing_id>")
def get_billings_id(billing_id: int) -> Response:
    api = BillingAPI()
    return api.get(billing_id, filters={Billing.user_id == current_user.id})


@api_v1_bp.patch("/billings/<int:billing_id>")
def patch_billings(billing_id: int) -> Response:
    def update_carts(s: Session, billing: Billing, data: dict) -> None:
        carts = s.query(Cart).filter_by(billing_id=billing.id).all()
        for cart in carts:
            country_code = billing.country.code
            is_business = billing.company is not None
            vat_rate, vat_reverse = get_vat(country_code, is_business)
            cart.currency_id = billing.country.currency_id
            cart.vat_rate = vat_rate
            cart.vat_reverse = vat_reverse
            s.flush()

    api = BillingAPI()
    api.raise_any_is_not_none({Order: {Order.billing_id == billing_id}})
    return api.patch(billing_id, post_calls=[update_carts])
