import json
import os

from web.helper.logger import logger


def sort_translations() -> None:
    # Create path to translations directory
    translations_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "translations",
    )
    # Get all paths to translation files
    paths = []
    for dir_path, _, filenames in os.walk(translations_dir):
        for filename in filenames:
            paths.append(os.path.join(dir_path, filename))
    # Sort all translation files
    for path in paths:
        with open(path, "r") as in_file:
            data_in = json.load(in_file)
        data_out = dict(sorted(data_in.items()))
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data_out, file, ensure_ascii=False, indent=4)
        logger.info(f"Sorted {path}")
