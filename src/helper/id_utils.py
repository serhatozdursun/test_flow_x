import secrets
import uuid


def generate_uuid():
    return str(uuid.uuid4())


def generate_id():
    return f"{secrets.randbelow(99999999 - 10000000 + 1) + 10000000}"
