from web.automation.fixture import (
    email_status_seeds,
    file_type_seeds,
    order_status_seeds,
    product_link_type_seeds,
    product_type_seeds,
    review_status_seeds,
    user_role_seeds,
)
from web.database import conn
from web.database.model import (
    AppSettings,
    EmailStatus,
    FileType,
    OrderStatus,
    ProductLinkType,
    ProductType,
    ReviewStatus,
    UserRole,
)

from ..automator import SeedSyncer


class AppSettingSeedSyncer(SeedSyncer):
    INTERVAL_S = 86400

    @classmethod
    def run(cls) -> None:
        with conn.begin() as s:
            if s.query(AppSettings).count() == 0:
                s.add(AppSettings())


class EmailStatusSeedSyncer(SeedSyncer):
    MODEL = EmailStatus
    KEY = "id"
    SEEDS = email_status_seeds


class FileTypeSeedSyncer(SeedSyncer):
    MODEL = FileType
    KEY = "id"
    SEEDS = file_type_seeds


class OrderStatusSeedSyncer(SeedSyncer):
    MODEL = OrderStatus
    KEY = "id"
    SEEDS = order_status_seeds


class ProductLinkeTypeSeedSyncer(SeedSyncer):
    MODEL = ProductLinkType
    KEY = "id"
    SEEDS = product_link_type_seeds


class ProductTypeSeedSyncer(SeedSyncer):
    MODEL = ProductType
    KEY = "id"
    SEEDS = product_type_seeds


class ReviewStatusSeedSyncer(SeedSyncer):
    MODEL = ReviewStatus
    KEY = "id"
    SEEDS = review_status_seeds


class UserRoleSeedSyncer(SeedSyncer):
    MODEL = UserRole
    KEY = "id"
    SEEDS = user_role_seeds
