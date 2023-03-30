from sqlalchemy import Column, String
from sqlalchemy.ext.hybrid import hybrid_property

from webshop.database.model._utils import FKRestrict
from . import Base
from .file_type import FileTypeId


class File(Base):
    __tablename__ = "file"

    desc = Column(String(64))
    path = Column(String(256), nullable=False, unique=True)
    type_id = Column(FKRestrict("file_type.id"), nullable=False)

    # Properties - types

    @hybrid_property
    def is_image(self) -> bool:
        return self.type_id == FileTypeId.IMAGE

    @hybrid_property
    def is_video(self) -> bool:
        return self.type_id == FileTypeId.VIDEO
