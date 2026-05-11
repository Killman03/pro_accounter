import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from utils.validators import normalize_kg_phone


FIELD_ALIASES = {
    "tenant": ("фио",),
    "model": ("модель",),
    "barcode": ("штрих", "штрих-код", "штрихкод"),
    "full_price": ("цена",),
    "rent_price": ("аренда",),
    "deposit": ("депозит", "залог"),
    "phone": ("телефон", "тел"),
    "start_date": ("дата первой оплаты", "дата"),
    "mark": ("отметка",),
    "comment": ("коммент", "комментарий"),
}


@dataclass
class ParsedChecklist:
    values: dict[str, Any]
    issues: list[str] = field(default_factory=list)
    raw_fields: dict[str, str] = field(default_factory=dict)

    @property
    def is_ready(self) -> bool:
        required = (
            "tenant",
            "model",
            "barcode",
            "rent_price",
            "deposit",
            "phone",
            "start_date",
        )
        return all(self.values.get(key) not in (None, "") for key in required) and not self.issues


def looks_like_checklist(text: str | None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return "чек" in lowered and "лист" in lowered


def parse_checklist_text(
    text: str,
    available_models: list[Any] | None = None,
    reference_date: date | None = None,
) -> ParsedChecklist:
    reference_date = reference_date or date.today()
    message_date = _extract_message_date(text)
    fields = _extract_fields(text)
    issues: list[str] = []
    values: dict[str, Any] = {
        "tenant": _clean_text(fields.get("tenant")),
        "model": _match_model(_clean_text(fields.get("model")), available_models or [], issues),
        "barcode": _normalize_barcode(fields.get("barcode"), issues),
        "full_price": _parse_money(fields.get("full_price"), "Цена", issues, required=False),
        "rent_price": _parse_money(fields.get("rent_price"), "Аренда", issues),
        "deposit": _parse_money(fields.get("deposit"), "Депозит", issues),
        "phone": _normalize_phone(fields.get("phone"), issues),
        "start_date": _parse_date_value(fields.get("start_date"), message_date or reference_date, issues),
        "in_1C": False,
        "status": "active",
        "buyout": False,
        "buyout_date": None,
        "payments": [],
        "deal_type": "Аренда",
    }

    comment_parts = []
    mark = _clean_text(fields.get("mark"))
    comment = _clean_text(fields.get("comment"))
    if mark:
        comment_parts.append(f"Отметка: {mark}")
    if comment:
        comment_parts.append(comment)
    values["comment"] = "; ".join(comment_parts) if comment_parts else None

    _require(values, "tenant", "ФИО", issues)
    _require(values, "model", "Модель", issues)
    _require(values, "barcode", "Штрих", issues)
    _require(values, "phone", "Телефон", issues)
    _require(values, "start_date", "Дата первой оплаты", issues)

    return ParsedChecklist(values=values, issues=issues, raw_fields=fields)


def build_checklist_preview(values: dict[str, Any], issues: list[str] | None = None) -> str:
    issue_text = ""
    if issues:
        issue_text = "\n\nНужны уточнения:\n" + "\n".join(f"- {issue}" for issue in issues)

    return (
        "Проверьте сделку:\n\n"
        f"ФИО: {values.get('tenant') or '-'}\n"
        f"Модель: {values.get('model') or '-'}\n"
        f"Штрих: {values.get('barcode') or '-'}\n"
        f"Цена: {_format_money(values.get('full_price'))}\n"
        f"Аренда: {_format_money(values.get('rent_price'))}\n"
        f"Депозит: {_format_money(values.get('deposit'))}\n"
        f"Телефон: {values.get('phone') or '-'}\n"
        f"Дата начала: {values.get('start_date') or '-'}\n"
        f"Комментарий: {values.get('comment') or '-'}"
        f"{issue_text}"
    )


def _extract_message_date(text: str) -> date | None:
    match = re.search(r"\[(\d{2})\.(\d{2})\.(\d{4})\s+\d{2}:\d{2}\]", text)
    if not match:
        return None
    day, month, year = map(int, match.groups())
    return date(year, month, day)


def _extract_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        line = line.replace("\xa0", " ").strip()
        if not line or line.startswith("[") or line.lower() == "чек лист":
            continue
        for key, aliases in FIELD_ALIASES.items():
            alias_pattern = "|".join(re.escape(alias) for alias in sorted(aliases, key=len, reverse=True))
            match = re.match(rf"(?i)^\s*(?:{alias_pattern})\s*[:\-]?\s*(.*)$", line)
            if match:
                fields[key] = match.group(1).strip()
                break
    return fields


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip(" -:\t")
    return cleaned or None


def _parse_money(value: str | None, label: str, issues: list[str], required: bool = True) -> float | None:
    cleaned = _clean_text(value)
    if not cleaned:
        if required:
            issues.append(f"{label} не указана")
        return None
    digits = re.sub(r"[^\d.,]", "", cleaned).replace(",", ".")
    try:
        return float(digits)
    except ValueError:
        issues.append(f"{label}: не удалось распознать сумму '{cleaned}'")
        return None


def _normalize_phone(value: str | None, issues: list[str]) -> str | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    normalized = normalize_kg_phone(cleaned)
    if normalized:
        return normalized

    digits = re.sub(r"\D", "", cleaned)
    if re.fullmatch(r"0\d{9}", digits):
        return f"996{digits[1:]}"

    issues.append(f"Телефон: не удалось привести к формату 996XXXXXXXXX ('{cleaned}')")
    return None


def _normalize_barcode(value: str | None, issues: list[str]) -> str | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    barcode = re.sub(r"\s+", "", cleaned).upper()
    if not barcode:
        issues.append("Штрих пустой")
        return None
    return barcode


def _parse_date_value(value: str | None, default_date: date, issues: list[str]) -> date | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return default_date
    lowered = cleaned.lower()
    if "сегодня" in lowered:
        return default_date
    if "день установки" in lowered:
        issues.append("Дата первой оплаты: укажите дату вместо 'в день установки'")
        return None

    match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", lowered)
    if match:
        day, month, year = map(int, match.groups())
        if year < 100:
            year += 2000
        try:
            return date(year, month, day)
        except ValueError:
            issues.append(f"Дата первой оплаты: некорректная дата '{cleaned}'")
            return None

    issues.append(f"Дата первой оплаты: не удалось распознать '{cleaned}'")
    return None


def _match_model(raw_model: str | None, available_models: list[Any], issues: list[str]) -> str | None:
    if not raw_model:
        return None
    normalized_raw = _normalize_model_text(raw_model)
    for model in available_models:
        name = getattr(model, "name", str(model))
        if _normalize_model_text(name) == normalized_raw:
            return name
    for model in available_models:
        name = getattr(model, "name", str(model))
        normalized_name = _normalize_model_text(name)
        if normalized_raw in normalized_name or normalized_name in normalized_raw:
            return name

    raw_numbers = set(re.findall(r"\d+", normalized_raw))
    if raw_numbers:
        matches = []
        for model in available_models:
            name = getattr(model, "name", str(model))
            if raw_numbers & set(re.findall(r"\d+", _normalize_model_text(name))):
                matches.append(name)
        if len(matches) == 1:
            return matches[0]

    issues.append(f"Модель: не найдена в справочнике ('{raw_model}')")
    return raw_model


def _normalize_model_text(value: str) -> str:
    return re.sub(r"[^a-zа-я0-9]+", "", value.lower())


def _require(values: dict[str, Any], key: str, label: str, issues: list[str]) -> None:
    if values.get(key) in (None, ""):
        message = f"{label} не указан"
        if message not in issues:
            issues.append(message)


def _format_money(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
