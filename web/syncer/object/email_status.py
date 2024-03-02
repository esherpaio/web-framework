from web.database.model import EmailStatus
from web.database.seed import email_status_seeds
from web.syncer import Syncer


class EmailStatusSyncer(Syncer):
    MODEL = EmailStatus
    KEY = "id"
    SEEDS = email_status_seeds
