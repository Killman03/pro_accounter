import re


def normalize_kg_phone(phone: str) -> str | None:
    """Очищает номер от нецифр и приводит к формату 996XXXXXXXXX (12 цифр)."""
    digits = re.sub(r"\D", "", phone or "")
    if re.fullmatch(r"996\d{9}", digits):
        return digits
    return None


def validate_kg_phone(phone: str) -> bool:
    return normalize_kg_phone(phone) is not None