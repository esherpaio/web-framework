from sqlalchemy import String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC

from ._base import Base


class Region(Base):
    __tablename__ = "region"

    name = MC(String(64), nullable=False, unique=True)

    # Properties - regions

    @hybrid_property
    def is_europe(self) -> bool:
        return self.name.lower() == "europe"
