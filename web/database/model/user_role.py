from enum import IntEnum

from sqlalchemy import Column, Integer, String

from . import Base


class UserRole(Base):
    __tablename__ = "user_role"

    level = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False, unique=True)


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
