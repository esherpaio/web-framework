from web.automation.fixture import user_role_seeds
from web.database.model import UserRole

from ..automator import SeedSyncer


class UserRoleSeedSyncer(SeedSyncer):
    MODEL = UserRole
    KEY = "id"
    SEEDS = user_role_seeds
