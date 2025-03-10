from enum import StrEnum


class MailEvent(StrEnum):
    ORDER_PAID = "order.paid"
    ORDER_RECEIVED = "order.received"
    ORDER_REFUNDED = "order.refunded"
    ORDER_SHIPPED = "order.shipped"
    USER_REQUEST_PASSWORD = "user.request_password"
    USER_REQUEST_VERIFICATION = "user.request_verification"
    WEBSITE_CONTACT = "website.contact"
    WEBSITE_BULK = "website.bulk"


class MailMethod(StrEnum):
    SMTP = "SMTP"
