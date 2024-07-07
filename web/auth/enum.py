from enum import StrEnum


class AuthType(StrEnum):
    NONE = "none"
    KEY = "key"
    JWT = "JWT"


class G(StrEnum):
    USER = "_user"
    USER_ID = "_user_id"
    USER_STORED = "_user_stored"
    AUTH_TYPE = "_auth_type"
