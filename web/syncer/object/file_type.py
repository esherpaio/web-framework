from web.database.model import FileType
from web.database.seed import file_type_seeds
from web.syncer import Syncer


class FileTypeSyncer(Syncer):
    MODEL = FileType
    KEY = "id"
    SEEDS = file_type_seeds
