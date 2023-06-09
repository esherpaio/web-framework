import json
import os

from web import config
from web.helper.logger import logger


class Translator:
    def __init__(self) -> None:
        self.translations = {}
        self._load()

    def _load(self) -> None:
        translations_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "translations",
        )
        for dir_, _, filenames in os.walk(translations_dir):
            for filename in filenames:
                path = os.path.abspath(os.path.join(dir_, filename))
                with open(path, "r") as file:
                    name, _ = os.path.splitext(filename)
                    self.translations[name] = json.loads(file.read())

    def translate(self, key: str, language: str = config.WEBSITE_LANGUAGE_CODE) -> str:
        try:
            return self.translations[language][key]
        except KeyError:
            logger.error(f"Translation for {key} not found")
            return "NA"


translator = Translator()
_ = translator.translate
