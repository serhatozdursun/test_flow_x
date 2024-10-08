import random
import uuid


def generate_uuid():
    return str(uuid.uuid4())


def generate_id():
    return f"{random.randint(10000000, 99999999)}"
