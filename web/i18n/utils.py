import json
import os


def sync_translations(language_in: str, language_out: str) -> None:
    """Synchronizes languages.
    
    Keys starting with `API_HTTP_` will not be translated.
    """

    # Load in translations
    in_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "translations",
        f"{language_in}.json",
    )
    with open(in_path, "r") as in_file:
        in_data = json.load(in_file)

    # Load out translations
    out_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "translations",
        f"{language_out}.json",
    )
    with open(out_path, "r") as out_file:
        out_data = json.load(out_file)

    # Copy current data
    data = {}
    data.update(out_data)

    # Remove unused keys
    in_keys = in_data.keys()
    for out_key in out_data.keys():
        if out_key not in in_keys:
            del data[out_key]

    # Add new keys
    out_keys = out_data.keys()
    for in_key, in_value in in_data.items():
        if in_key.startswith("API_HTTP_"):
            continue
        if in_key not in out_keys:
            data[in_key] = in_value

    # Sort data by key
    data = dict(sorted(data.items()))

    # Write new data
    with open(out_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    sync_translations("en", "nl")
