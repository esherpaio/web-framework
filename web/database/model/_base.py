from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import declarative_base


class _Model:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


Base = declarative_base(cls=_Model)
