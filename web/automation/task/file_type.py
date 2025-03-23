from web.automation.fixture import file_type_seeds
from web.database.model import FileType

from ..automator import SeedSyncer


class FileTypeSeedSyncer(SeedSyncer):
    MODEL = FileType
    KEY = "id"
    SEEDS = file_type_seeds
