from enum import StrEnum
from typing import Callable

from web.helper.builtins import Singleton
from web.mail.routes.contact import send_contact_business, send_contact_customer
from web.mail.routes.order import (
    send_order_paid,
    send_order_received,
    send_order_refunded,
    send_order_shipped,
)
from web.mail.routes.user import send_new_password, send_verification_url

#
# Classes
#


class MailEvent(StrEnum):
    ORDER_PAID = "order.paid"
    ORDER_RECEIVED = "order.received"
    ORDER_REFUNDED = "order.refunded"
    ORDER_SHIPPED = "order.shipped"
    USER_REQUEST_PASSWORD = "user.request_password"
    USER_REQUEST_VERIFICATION = "user.request_verification"
    WEBSITE_CONTACT = "website.contact"


class Mail(metaclass=Singleton):
    def __init__(self) -> None:
        self.events: dict[MailEvent, list[Callable]] = {
            MailEvent.ORDER_PAID: [send_order_paid],
            MailEvent.ORDER_RECEIVED: [send_order_received],
            MailEvent.ORDER_REFUNDED: [send_order_refunded],
            MailEvent.ORDER_SHIPPED: [send_order_shipped],
            MailEvent.USER_REQUEST_PASSWORD: [send_new_password],
            MailEvent.USER_REQUEST_VERIFICATION: [send_verification_url],
            MailEvent.WEBSITE_CONTACT: [send_contact_business, send_contact_customer],
        }


#
# Variables
#

mail = Mail()
