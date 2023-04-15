from sqlalchemy.orm import Session

from webshop.database.client import conn
from webshop.database.model import FileType
from webshop.database.seeds import file_type_seeds
from webshop.seeder.abc import Syncer


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
