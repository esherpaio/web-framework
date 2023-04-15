from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base

from ._utils import current_time


class _Model:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=current_time)
    updated_at = Column(DateTime, onupdate=current_time)


Base = declarative_base(cls=_Model)
