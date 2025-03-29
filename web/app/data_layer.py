import json
from enum import StrEnum

from markupsafe import Markup

from web.api import JsonEncoder

#
# Triggers
#


class On(StrEnum):
    LOAD = "load"
    CLICK = "click"
    SUBMIT = "submit"


class By:
    def js_function(self, name: str, data: dict | None = None) -> str:
        if data is None:
            data = {}
        data["event"] = name
        value = json.dumps(data, cls=JsonEncoder)
        return f"dataLayer.push({value});"

    def js_callable(self, name: str, data: dict | None = None) -> str:
        func = self.js_function(name, data)
        return f"function (e) {{ {func} }}"

    def js_listener(self, *args, **kwargs) -> str:
        raise NotImplementedError


class ByWindow(By):
    def __init__(self, on: On) -> None:
        self.on = on

    def js_listener(self, name: str, data: dict | None = None) -> str:
        func = self.js_function(name, data)
        return Markup(func)


class ById(By):
    def __init__(self, on: On, id_: str) -> None:
        self.on = on
        self.id_ = id_

    def js_listener(self, name: str, data: dict | None = None) -> str:
        call = self.js_callable(name, data)
        return Markup(
            f"document.getElementById('{self.id_}').addEventListener('{self.on}', {call});"
        )


class ByClass(By):
    def __init__(self, on: On, class_: str | None = None) -> None:
        self.on = on
        self.class_ = class_

    def js_listener(self, name: str, data: dict | None = None) -> str:
        if self.class_ is None:
            class_ = f"event-{name}"
        call = self.js_callable(name, data)
        return Markup(
            f"[...document.getElementsByClassName('{class_}')].forEach((e) => {{ e.addEventListener('{self.on}', {call}) }});"
        )


#
# Events
#


class Event:
    NAME: str

    def __init__(self, by: By) -> None:
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


class Events:
    def __init__(self, *events: Event) -> None:
        self._events = events

    def __bool__(self) -> bool:
        return bool(self._events)

    def __add__(self, other: "Events") -> "Events":
        return Events(*(self._events + other._events))

    def __iadd__(self, other: "Events") -> "Events":
        self._events += other._events
        return self

    @property
    def code(self) -> Markup:
        codes = " \n".join([x.code for x in self._events])
        return Markup(
            f"<script>window.addEventListener('load', () => {{ {codes} }});</script>"
        )


class EventSignUp(Event):
    NAME = "sign_up"


class EventLogin(Event):
    NAME = "login"


class EventViewItemList(Event):
    NAME = "view_item_list"


class EventViewItem(Event):
    NAME = "view_item"


class EventAddToCart(Event):
    NAME = "add_to_cart"


class EventViewCart(Event):
    NAME = "view_cart"


class EventRemoveFromCart(Event):
    NAME = "remove_from_cart"


class EventBeginCheckout(Event):
    NAME = "begin_checkout"


class EventAddShippingInfo(Event):
    NAME = "add_shipping_info"


class EventAddPaymentInfo(Event):
    NAME = "add_payment_info"


class EventPurchase(Event):
    NAME = "purchase"
