from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase
from .file_type import FileTypeId


class File(IntBase):
    __tablename__ = "file"

    description = MC(String(64))
    path = MC(String(256), nullable=False, unique=True)

    type_id = MC(ForeignKey("file_type.id", ondelete="RESTRICT"), nullable=False)

    # Properties - types

    @hybrid_property
    def is_image(self) -> bool:
        return self.type_id == FileTypeId.IMAGE

    @hybrid_property
    def is_video(self) -> bool:
        return self.type_id == FileTypeId.VIDEO
