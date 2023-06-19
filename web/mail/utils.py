import base64


def pdf_to_string(path: str, encode: bool = False) -> str:
    with open(path, "rb") as file:
        data = file.read()
    if encode:
        return base64.b64encode(data).decode()
    return data


if __name__ == "__main__":
    path_ = "/Users/stan/Downloads/test.pdf"
    print(pdf_to_string(path_))
