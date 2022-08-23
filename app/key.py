from secrets import token_bytes


def secret_key() -> bytes:
    try:
        with open(".SECRET_KEY", mode="rb") as reader:
            key = reader.read()

        if len(key) != 32:
            raise ValueError
    except (FileNotFoundError, ValueError):
        key = token_bytes(32)
        with open(".SECRET_KEY", mode="wb") as writer:
            writer.write(key)

    return key
