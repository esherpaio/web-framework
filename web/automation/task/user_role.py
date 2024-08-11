from web.automation.seed import user_role_seeds
from web.database.model import UserRole

from ..syncer import Syncer


class UserRoleSyncer(Syncer):
    MODEL = UserRole
    KEY = "id"
    SEEDS = user_role_seeds
