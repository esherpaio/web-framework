from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import declarative_base

# todo: add support for mypy
# info: https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#whatsnew-20-orm-declarative-typing


class Model:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


Base = declarative_base(cls=Model)
