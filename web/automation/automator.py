from typing import Type

from sqlalchemy.orm import Session

from web.database.model import Base


class Automator:
    MODEL: Type[Base]

    @classmethod
    def run(cls, s: Session) -> None:
        raise NotImplementedError
