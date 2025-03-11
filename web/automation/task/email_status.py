from web.automation.fixture import email_status_seeds
from web.database.model import EmailStatus

from ..automator import SeedSyncer


class EmailStatusSeedSyncer(SeedSyncer):
    MODEL = EmailStatus
    KEY = "id"
    SEEDS = email_status_seeds
