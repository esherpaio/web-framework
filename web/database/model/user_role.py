from enum import IntEnum, StrEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column as MC

from ._base import StrBase


class UserRole(StrBase):
    __tablename__ = "user_role"

    level = MC(Integer, nullable=False)
    name = MC(String(64), nullable=False, unique=True)


class UserRoleId(StrEnum):
    GUEST = "guest"
    USER = "user"
    EXTERNAL = "external"
    ADMIN = "admin"
    SUPER = "super"


class UserRoleLevel(IntEnum):
    GUEST = 100
    USER = 200
    EXTERNAL = 250
    ADMIN = 300
    SUPER = 400
