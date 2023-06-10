import json
import os

from flask import has_request_context, request
from flask_login import current_user

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

    @property
    def language_code() -> str:
        if has_request_context():
            return current_user.language.code
        elif config.WEBSITE_LANGUAGE_CODE:
            return config.WEBSITE_LANGUAGE_CODE
        else:
            return "en"

    def translate(self, key: str) -> str:
        try:
            return self.translations[self.language_code][key]
        except KeyError:
            logger.error(f"Translation for {key} not found")
            return "NA"


translator = Translator()
_ = translator.translate
