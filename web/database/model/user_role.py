from enum import IntEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column as MC

from . import Base


class UserRole(Base):
    __tablename__ = "user_role"

    level = MC(Integer, nullable=False)
    name = MC(String(64), nullable=False, unique=True)


class UserRoleId(IntEnum):
    GUEST = 1
    USER = 2
    ADMIN = 3
    SUPER = 4


class UserRoleLevel(IntEnum):
    GUEST = 100
    USER = 200
    ADMIN = 300
    SUPER = 400
