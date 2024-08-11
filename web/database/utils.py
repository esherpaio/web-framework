from sqlalchemy.orm import Session

from .model import Base


def copy_row(s: Session, row: Base, new: Base) -> Base:
    for k, v in row.__dict__.items():
        if k == "id" or k.startswith("_"):
            continue
        setattr(new, k, v)
    s.add(new)
    return new
