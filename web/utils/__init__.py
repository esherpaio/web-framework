from .generators import gen_slug
from .getters import none_attrgetter
from .obfuscation import obfuscate_data
from .singleton import Singleton
from .storage import remove_file
from .validation import is_email, is_phone

__all__ = [
    "gen_slug",
    "is_email",
    "is_phone",
    "none_attrgetter",
    "obfuscate_data",
    "remove_file",
    "Singleton",
]
