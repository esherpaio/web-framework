import json
import os

from flask import has_request_context

from web.config import config
from web.locale import current_locale
from web.logger import log
from web.utils import Singleton


class Translator(metaclass=Singleton):
    fallback_translation = "NA"
    fallback_language_code = "en"

    def __init__(self) -> None:
        self.translations: dict = {}
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = os.path.join(cur_dir, "translation")
        self.load_dir(root_dir)

    def load_dir(self, dir_: str) -> None:
        dir_ = os.path.abspath(dir_)
        for fd, _, fns in os.walk(dir_):
            for fn in fns:
                fp = os.path.abspath(os.path.join(fd, fn))
                self.load_file(fp)

    def load_file(self, fp: str) -> None:
        with open(fp, "r") as f:
            data = f.read()
        fn, fext = os.path.splitext(os.path.basename(fp))
        if fext != ".json":
            return
        if fn not in self.translations:
            self.translations[fn] = {}
        self.translations[fn].update(json.loads(data))

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
        if config.WEBSITE_LANGUAGE_CODE:
            return config.WEBSITE_LANGUAGE_CODE
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
