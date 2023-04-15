from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import UserRole
from web.database.seeds import user_role_seeds
from web.seeder.abc import Syncer


class UserRoleSyncer(Syncer):
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in user_role_seeds:
            row = s.query(UserRole).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        UserRoleSyncer().sync(s_)
