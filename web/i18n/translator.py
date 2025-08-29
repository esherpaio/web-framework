import json
import os

from flask import has_request_context

from web.locale import current_locale
from web.logger import log
from web.setup import config
from web.utils import Singleton


class Translator(metaclass=Singleton):
    fallback_translation = "NA"
    fallback_language_code = "en"

    def __init__(self) -> None:
        self.translations: dict = {}
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = os.path.join(cur_dir, "translation")
        self.load_dir(root_dir)

    def load_dir(self, dir_: str) -> int:
        total = 0
        dir_ = os.path.abspath(dir_)
        for fd, _, fns in os.walk(dir_):
            for fn in fns:
                fp = os.path.abspath(os.path.join(fd, fn))
                result = self.load_file(fp)
                if result:
                    total += 1
        return total

    def load_file(self, fp: str) -> bool:
        with open(fp, "r") as f:
            data_str = f.read()
        fbn = os.path.basename(fp)
        fn, fext = os.path.splitext(fbn)
        if fext != ".json":
            return False
        if fn not in self.translations:
            self.translations[fn] = {}
        data = json.loads(data_str)
        if data:
            self.translations[fn].update(data)
        return bool(data)

    def get_translations(self, language_code: str) -> dict:
        try:
            return self.translations[language_code]
        except KeyError:
            log.error(f"Translations for {language_code} not found")
            raise

    @property
    def language_code(self) -> str:
        if has_request_context():
            try:
                language = current_locale.language
            except Exception:
                log.error("Unable to get language from locale")
            else:
                return language.code
        if config.LOCALE_LANGUAGE_CODE:
            return config.LOCALE_LANGUAGE_CODE
        return self.fallback_language_code

    def translate_strict(self, key: str, **kwargs) -> str | None:
        try:
            translations = self.get_translations(self.language_code)
            text = translations[key] % kwargs
        except KeyError:
            log.error(f"Translation for {key}:{kwargs} has failed", exc_info=True)
            return None
        else:
            return text

    def translate(self, key: str, **kwargs) -> str:
        text = self.translate_strict(key, **kwargs)
        if text is not None:
            return text
        return self.fallback_translation


translator = Translator()
_ = translator.translate
