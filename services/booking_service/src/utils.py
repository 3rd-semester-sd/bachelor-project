
import random
import string


def redis_confirmation_key(confirmation_code: str) -> str:
    return f"booking:{confirmation_code}:confirmation_code"


def generate_confirmation_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
