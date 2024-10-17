import re

def validate_phone_number(phone: str) -> bool:
    return bool(re.fullmatch(r"\+?[0-9]{10,15}", phone))

