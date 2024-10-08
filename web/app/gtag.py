import json
from enum import StrEnum

from markupsafe import Markup


class EventType(StrEnum):
    ON_LOAD = "load"
    ON_CLICK = "click"


class EventName(StrEnum):
    SIGN_UP = "sign_up"
    LOGIN = "login"
    VIEW_ITEM_LIST = "view_item_list"
    VIEW_ITEM = "view_item"
    ADD_TO_CART = "add_to_cart"
    VIEW_CART = "view_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    BEGIN_CHECKOUT = "begin_checkout"
    ADD_SHIPPING_INFO = "add_shipping_info"
    ADD_PAYMENT_INFO = "add_payment_info"
    PURCHASE = "purchase"


class GTagEvent:
    """A class to generate Google tags code."""

    NAME: str

    def __init__(self, id_: str, type_: EventType) -> None:
        self.id = id_
        self.type = type_
        self._data: dict = {}

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, data: dict) -> None:
        for key, value in data.copy().items():
            if value is None:
                data.pop(key)
        self._data = data

    @property
    def code(self) -> Markup:
        return Markup(self._js_listener)

    @property
    def _js_listener(self) -> Markup:
        return Markup(
            f"document.getElementById('{self.id}').addEventListener('{self.type}', {self.js_push_func});"
        )

    @property
    def js_push_func(self) -> Markup:
        return Markup(
            f"function (e) {{ gtag('event', '{self.NAME}', {json.dumps(self.data)}); }}"
        )


class GTagSignUp(GTagEvent):
    NAME = "sign_up"


class GTagLogin(GTagEvent):
    NAME = "login"


class GTagViewItemList(GTagEvent):
    NAME = "view_item_list"


class GTagViewItem(GTagEvent):
    NAME = "view_item"


class GTagAddToCart(GTagEvent):
    NAME = "add_to_cart"


class GTagViewCart(GTagEvent):
    NAME = "view_cart"


class GTagRemoveFromCart(GTagEvent):
    NAME = "remove_from_cart"


class GTagBeginCheckout(GTagEvent):
    NAME = "begin_checkout"


class GTagAddShippingInfo(GTagEvent):
    NAME = "add_shipping_info"


class GTagAddPaymentInfo(GTagEvent):
    NAME = "add_payment_info"


class GTagPurchase(GTagEvent):
    NAME = "purchase"


def gen_gtags(gtags: list[GTagEvent] | None = None) -> list[GTagEvent]:
    if gtags is None:
        gtags = []
    return gtags
