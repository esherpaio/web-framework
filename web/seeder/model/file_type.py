from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import FileType
from web.database.seeds import file_type_seeds
from web.seeder.abc import Syncer


class FileTypeSyncer(Syncer):
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in file_type_seeds:
            row = s.query(FileType).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        FileTypeSyncer().sync(s_)
