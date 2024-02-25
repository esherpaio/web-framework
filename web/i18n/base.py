import json
import os

from web.config import config
from web.libs.locale import current_locale
from web.libs.logger import log
from web.libs.utils import Singleton


class Translator(metaclass=Singleton):
    fallback_translation = "NA"
    fallback_language_code = "en"

    def __init__(self) -> None:
        self.translations: dict = {}
        self._load()

    def _load(self) -> None:
        translations_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "translation",
        )
        for dir_, _, filenames in os.walk(translations_dir):
            for filename in filenames:
                path = os.path.abspath(os.path.join(dir_, filename))
                self.add(path)

    def add(self, path: str) -> None:
        with open(path, "r") as file:
            name, _ = os.path.splitext(os.path.basename(path))
            if name not in self.translations:
                self.translations[name] = {}
            self.translations[name].update(json.loads(file.read()))

    @property
    def language_code(self) -> str:
        if current_locale and current_locale.language:
            return current_locale.language.code
        elif config.WEBSITE_LANGUAGE_CODE:
            return config.WEBSITE_LANGUAGE_CODE
        else:
            return self.fallback_language_code

    def translate(self, key: str, **kwargs) -> str:
        # Try to find translations for language codes
        for language_code in [self.language_code, self.fallback_language_code]:
            try:
                translations = self.translations[language_code]
                break
            except KeyError:
                log.error(f"Translations for {language_code} not found")
        else:
            return self.fallback_translation
        # Try to find translation for key
        try:
            text = translations[key]
        except KeyError:
            log.error(f"Translation for {key} not found")
            return self.fallback_translation
        # Try to fill in keyword arguments
        try:
            return text % kwargs
        except KeyError:
            log.error(f"Translation for {key} is missing arguments")
            return self.fallback_translation


translator = Translator()
_ = translator.translate
