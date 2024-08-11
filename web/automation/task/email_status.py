from web.automation.seed import email_status_seeds
from web.database.model import EmailStatus

from .. import Syncer


class EmailStatusSyncer(Syncer):
    MODEL = EmailStatus
    KEY = "id"
    SEEDS = email_status_seeds
