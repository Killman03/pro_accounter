import secrets
from datetime import date, datetime, time, timedelta, timezone

KG_TZ = timezone(timedelta(hours=6))
_last_meta_event_ts = 0


def build_unique_meta_event_time(value: date | datetime | None) -> datetime:
    """
    Возвращает уникальное время события в timezone +06:00.
    Формат для сериализации: YYYY-MM-DDTHH:MM:SS+06:00
    """
    global _last_meta_event_ts

    if isinstance(value, datetime):
        base_date = value.astimezone(KG_TZ).date() if value.tzinfo else value.date()
    elif isinstance(value, date):
        base_date = value
    else:
        base_date = datetime.now(KG_TZ).date()

    random_second = secrets.randbelow(24 * 60 * 60)
    candidate = datetime.combine(base_date, time(0, 0, 0), tzinfo=KG_TZ) + timedelta(seconds=random_second)
    ts = int(candidate.timestamp())
    if ts <= _last_meta_event_ts:
        ts = _last_meta_event_ts + 1
    _last_meta_event_ts = ts
    return datetime.fromtimestamp(ts, KG_TZ)
