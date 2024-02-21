from enum import StrEnum
from typing import Callable

from web.libs.logger import log
from web.libs.utils import Singleton
from web.mail.events import (
    mail_contact_business,
    mail_contact_customer,
    mail_mass,
    mail_order_paid,
    mail_order_received,
    mail_order_refunded,
    mail_order_shipped,
    mail_user_password,
    mail_user_verification,
)

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
    WEBSITE_MASS = "website.mass"


class _Mail(metaclass=Singleton):
    def __init__(self) -> None:
        self.events: dict[MailEvent | str, list[Callable]] = {
            MailEvent.ORDER_PAID: [mail_order_paid],
            MailEvent.ORDER_RECEIVED: [mail_order_received],
            MailEvent.ORDER_REFUNDED: [mail_order_refunded],
            MailEvent.ORDER_SHIPPED: [mail_order_shipped],
            MailEvent.USER_REQUEST_PASSWORD: [mail_user_password],
            MailEvent.USER_REQUEST_VERIFICATION: [mail_user_verification],
            MailEvent.WEBSITE_CONTACT: [mail_contact_business, mail_contact_customer],
            MailEvent.WEBSITE_MASS: [mail_mass],
        }

    def get_events(self, event: MailEvent | str) -> list[Callable]:
        events = self.events.get(event, [])
        if not events:
            log.error(f"Event {event} not found")
        return events


#
# Variables
#

mail = _Mail()
