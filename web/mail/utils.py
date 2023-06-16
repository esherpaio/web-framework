import base64


def pdf_to_string(path: str) -> str:
    with open(path, "rb") as file:
        data = file.read()
    return base64.b64encode(data).decode()
