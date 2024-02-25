from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import FileType
from web.database.seed import file_type_seeds
from web.seeder.abc import Syncer


class FileTypeSyncer(Syncer):
    def __init__(self, seeds: list[FileType] = file_type_seeds) -> None:
        super().__init__()
        self.seeds: list[FileType] = seeds

    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in self.seeds:
            row = s.query(FileType).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        FileTypeSyncer().sync(s_)
