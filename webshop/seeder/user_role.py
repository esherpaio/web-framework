from sqlalchemy.orm import Session

from webshop.database.client import Conn
from webshop.database.model import UserRole
from webshop.database.seeds import user_role_seeds
from webshop.helper.seeder import Syncer


class UserRoleSyncer(Syncer):
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in user_role_seeds:
            row = s.query(UserRole).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with Conn.begin() as s_:
        UserRoleSyncer().sync(s_)
