import json
import os

from web.config import config
from web.locale import current_locale
from web.logger import log
from web.utils import Singleton


class Translator(metaclass=Singleton):
    fallback_translation = "NA"
    fallback_language_code = "en"

    def __init__(self) -> None:
        self.translations: dict = {}
        self.load_translations()

    def load_translations(self) -> None:
        translations_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "translation",
        )
        for dir_, _, filenames in os.walk(translations_dir):
            for filename in filenames:
                path = os.path.abspath(os.path.join(dir_, filename))
                self.add_translations(path)

    def add_translations(self, path: str) -> None:
        with open(path, "r") as file:
            name, _ = os.path.splitext(os.path.basename(path))
            if name not in self.translations:
                self.translations[name] = {}
            self.translations[name].update(json.loads(file.read()))

    def get_translations(self, language_code: str) -> dict:
        try:
            return self.translations[language_code]
        except KeyError:
            log.error(f"Translations for {language_code} not found")
            raise

    @property
    def language_code(self) -> str:
        if current_locale and current_locale.language:
            return current_locale.language.code
        elif config.WEBSITE_LANGUAGE_CODE:
            return config.WEBSITE_LANGUAGE_CODE
        else:
            return self.fallback_language_code

    def translate_strict(self, key: str, **kwargs) -> str | None:
        try:
            translations = self.get_translations(self.language_code)
            text = translations[key] % kwargs
        except KeyError:
            log.error(f"Translation for {key}:{kwargs} has failed")
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
