from typing import Callable

from web.mail import MailEvent, event

mail_events: dict[MailEvent | str, list[Callable]] = {
    MailEvent.ORDER_PAID: [event.mail_order_paid],
    MailEvent.ORDER_RECEIVED: [event.mail_order_received],
    MailEvent.ORDER_REFUNDED: [event.mail_order_refunded],
    MailEvent.ORDER_SHIPPED: [event.mail_order_shipped],
    MailEvent.USER_REQUEST_PASSWORD: [event.mail_user_password],
    MailEvent.USER_REQUEST_VERIFICATION: [event.mail_user_verification],
    MailEvent.WEBSITE_CONTACT: [event.mail_contact_business],
    MailEvent.WEBSITE_BULK: [event.mail_bulk],
}
