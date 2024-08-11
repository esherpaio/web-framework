from web.automation.seed import file_type_seeds
from web.database.model import FileType

from .. import Syncer


class FileTypeSyncer(Syncer):
    MODEL = FileType
    KEY = "id"
    SEEDS = file_type_seeds
