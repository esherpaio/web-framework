import json
from enum import StrEnum

from markupsafe import Markup

#
# Events
#


class EventTrigger(StrEnum):
    ON_LOAD = "load"
    ON_CLICK = "click"


class Event:
    def js_listener(self, *args, **kwargs) -> str:
        raise NotImplementedError

    def js_function(self, name: str, data: dict | None = None) -> str:
        if data is None:
            data = {}
        return f"function (e) {{ gtag('event', '{name}', {json.dumps(data)}); }}"


class EventByWindow(Event):
    def __init__(self, trigger: EventTrigger) -> None:
        self.trigger = trigger

    def js_listener(self, name: str, data: dict | None = None) -> str:
        function = self.js_function(name, data)
        return Markup(f"window.addEventListener('{self.trigger}', {function});")


class EventById(Event):
    def __init__(self, element_id: str, trigger: EventTrigger) -> None:
        self.id_ = element_id
        self.trigger = trigger

    def js_listener(self, name: str, data: dict | None = None) -> str:
        function = self.js_function(name, data)
        return Markup(
            f"document.getElementById('{self.id_}').addEventListener('{self.trigger}', {function});"
        )


#
# Google tags
#


class Gtag:
    NAME: str

    def __init__(self, by: Event) -> None:
        self.by = by
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
        return Markup(self.by.js_listener(self.NAME, self.data))


class GtagSignUp(Gtag):
    NAME = "sign_up"


class GtagLogin(Gtag):
    NAME = "login"


class GtagViewItemList(Gtag):
    NAME = "view_item_list"


class GtagViewItem(Gtag):
    NAME = "view_item"


class GtagAddToCart(Gtag):
    NAME = "add_to_cart"


class GtagViewCart(Gtag):
    NAME = "view_cart"


class GtagRemoveFromCart(Gtag):
    NAME = "remove_from_cart"


class GtagBeginCheckout(Gtag):
    NAME = "begin_checkout"


class GtagAddShippingInfo(Gtag):
    NAME = "add_shipping_info"


class GtagAddPaymentInfo(Gtag):
    NAME = "add_payment_info"


class GtagPurchase(Gtag):
    NAME = "purchase"


#
# Utilities
#


def gen_gtags(gtags: list[Gtag] | None = None) -> list[Gtag]:
    if gtags is None:
        gtags = []
    return gtags
