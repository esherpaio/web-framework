from web.automation.fixture import review_status_seeds
from web.database.model import ReviewStatus

from ..automator import SeedSyncer


class ReviewStatusSeedSyncer(SeedSyncer):
    MODEL = ReviewStatus
    KEY = "id"
    SEEDS = review_status_seeds
