import re

def validate_kg_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"996\d{9}", phone)) 