import base64


def file_to_str(path: str, encode: bool = False) -> str:
    with open(path, "rb") as file:
        data = file.read()
    if encode:
        return base64.b64encode(data).decode()
    return data
