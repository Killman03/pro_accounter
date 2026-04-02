import secrets
from datetime import date, datetime, time, timedelta, timezone

KG_TZ = timezone(timedelta(hours=6))
_used_seconds_by_date: dict[str, set[int]] = {}


def build_unique_meta_event_time(value: date | datetime | None) -> datetime:
    """
    Возвращает уникальное время события в timezone +06:00.
    Формат для сериализации: YYYY-MM-DDTHH:MM:SS+06:00
    """
    if isinstance(value, datetime):
        base_date = value.astimezone(KG_TZ).date() if value.tzinfo else value.date()
    elif isinstance(value, date):
        base_date = value
    else:
        base_date = datetime.now(KG_TZ).date()

    day_key = base_date.isoformat()
    used_seconds = _used_seconds_by_date.setdefault(day_key, set())

    second_of_day = secrets.randbelow(24 * 60 * 60)
    if second_of_day in used_seconds:
        for candidate_second in range(24 * 60 * 60):
            if candidate_second not in used_seconds:
                second_of_day = candidate_second
                break
    used_seconds.add(second_of_day)

    return datetime.combine(base_date, time(0, 0, 0), tzinfo=KG_TZ) + timedelta(seconds=second_of_day)
