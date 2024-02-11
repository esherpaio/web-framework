from .order import (
    mail_order_paid,
    mail_order_received,
    mail_order_refunded,
    mail_order_shipped,
)
from .user import mail_user_password, mail_user_verification
from .website import mail_contact_business, mail_contact_customer

__all__ = [
    "mail_order_paid",
    "mail_order_received",
    "mail_order_refunded",
    "mail_order_shipped",
    "mail_user_password",
    "mail_user_verification",
    "mail_contact_business",
    "mail_contact_customer",
]
