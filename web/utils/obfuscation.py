OBFUSCATE_PARTIAL: set[str] = {"password"}
OBFUSCATE_MATCH: set[str] = {"email", "phone", "address", "last_name", "vat"}


def obfuscate_data(data: dict | list) -> dict | list:
    if isinstance(data, dict):
        for key in list(data.keys()):
            if any(x for x in OBFUSCATE_PARTIAL if x in key):
                data[key] = "[obfuscated]"
            if key in OBFUSCATE_MATCH:
                data[key] = "[obfuscated]"
            else:
                data[key] = obfuscate_data(data[key])
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = obfuscate_data(data[i])
    return data
