import json
from enum import StrEnum

from markupsafe import Markup

from web.api import JsonEncoder

#
# Events
#


class EventTrigger(StrEnum):
    ON_LOAD = "load"
    ON_CLICK = "click"
    ON_SUBMIT = "submit"


class Event:
    def js_function(self, name: str, data: dict | None = None) -> str:
        if data is None:
            data = {}
        value = json.dumps(data, cls=JsonEncoder)
        return f"gtag('event', '{name}', {value});"

    def js_callable(self, name: str, data: dict | None = None) -> str:
        func = self.js_function(name, data)
        return f"function (e) {{ {func} }}"

    def js_listener(self, *args, **kwargs) -> str:
        raise NotImplementedError


class EventByWindow(Event):
    def __init__(self, trigger: EventTrigger) -> None:
        self.trigger = trigger

    def js_listener(self, name: str, data: dict | None = None) -> str:
        func = self.js_function(name, data)
        return Markup(func)


class EventById(Event):
    def __init__(self, trigger: EventTrigger, id_: str) -> None:
        self.trigger = trigger
        self.id_ = id_

    def js_listener(self, name: str, data: dict | None = None) -> str:
        call = self.js_callable(name, data)
        return Markup(
            f"document.getElementById('{self.id_}').addEventListener('{self.trigger}', {call});"
        )


class EventByClass(Event):
    def __init__(self, trigger: EventTrigger, class_: str | None = None) -> None:
        self.trigger = trigger
        self.class_ = class_

    def js_listener(self, name: str, data: dict | None = None) -> str:
        if self.class_ is None:
            class_ = f"gtag-{name}"
        call = self.js_callable(name, data)
        return Markup(
            f"[...document.getElementsByClassName('{class_}')].forEach((e) => {{ e.addEventListener('{self.trigger}', {call}) }});"
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


class Gtags:
    def __init__(self, *gtags: Gtag) -> None:
        self._gtags = gtags

    @property
    def code(self) -> Markup:
        codes = " \n".join([x.code for x in self._gtags])
        return Markup(
            f"<script>window.addEventListener('load', () => {{ {codes} }});</script>"
        )


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
