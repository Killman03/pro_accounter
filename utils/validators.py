import re


def normalize_kg_phone(phone: str) -> str | None:
    """Очищает номер от нецифр и приводит к формату 996XXXXXXXXX (12 цифр)."""
    if not phone:
        return None
    # Разрешаем только цифры и базовые разделители, но не буквы.
    if re.search(r"[^\d\s+()-]", phone):
        return None

    digits = re.sub(r"\D", "", phone or "")
    if re.fullmatch(r"996\d{9}", digits):
        return digits
    return None


def normalize_kg_phone_with_plus(phone: str) -> str | None:
    normalized = normalize_kg_phone(phone)
    if not normalized:
        return None
    return f"+{normalized}"


def validate_kg_phone(phone: str) -> bool:
    return normalize_kg_phone(phone) is not None
