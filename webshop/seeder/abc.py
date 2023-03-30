from abc import ABCMeta, abstractmethod

from sqlalchemy.orm import Session


class Syncer(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def sync(s: Session) -> None:
        """Run a synchronizing function"""

        pass


class Seeder(metaclass=ABCMeta):
    @abstractmethod
    def seed(self, s: Session, count: int = 1) -> None:
        """Run a seeding function"""

        pass
