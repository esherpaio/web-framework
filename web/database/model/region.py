from sqlalchemy import Column, String
from sqlalchemy.ext.hybrid import hybrid_property

from . import Base


class Region(Base):
    __tablename__ = "region"

    name = Column(String(64), nullable=False, unique=True)

    # Properties - regions

    @hybrid_property
    def is_europe(self) -> bool:
        return self.name.lower() == "europe"
