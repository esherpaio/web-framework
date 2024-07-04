from web.database.model import UserRole
from web.database.seed import user_role_seeds

from ..syncer import Syncer


class UserRoleSyncer(Syncer):
    MODEL = UserRole
    KEY = "id"
    SEEDS = user_role_seeds
