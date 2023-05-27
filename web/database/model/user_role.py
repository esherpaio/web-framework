from enum import IntEnum

from sqlalchemy import Column, Integer, String

from . import Base


class UserRole(Base):
    __tablename__ = "user_role"

    level = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False, unique=True)


class UserRoleId(IntEnum):
    USER = 1
    ADMIN = 2
    SUPER = 3


class UserRoleLevel(IntEnum):
    USER = 100
    ADMIN = 500
    SUPER = 900
