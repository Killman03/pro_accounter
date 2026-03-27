import hashlib
import logging
import re
from datetime import date, datetime, timezone
from time import time
from typing import Any, Mapping, Optional

import aiohttp

from config import (
    META_CAPI_ACCESS_TOKEN,
    META_CAPI_API_VERSION,
    META_CAPI_DATASET_ID,
    META_CAPI_LEAD_EVENT_SOURCE,
    META_CAPI_TEST_EVENT_CODE,
)

logger = logging.getLogger(__name__)


def _sha256_normalized(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()


def _normalize_phone(phone: str) -> str:
    return re.sub(r"\D+", "", phone or "")


def _split_name(full_name: str) -> tuple[str, str]:
    parts = (full_name or "").strip().split()
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def _enabled() -> bool:
    return bool(META_CAPI_ACCESS_TOKEN and META_CAPI_DATASET_ID)


def _to_unix_timestamp(value: Any) -> int:
    if value is None:
        return int(time())
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return int(value.timestamp())
    if isinstance(value, date):
        dt = datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
        return int(dt.timestamp())
    return int(time())


async def send_new_user_to_meta_capi(
    machine_data: Mapping[str, Any],
    lead_id: Optional[int] = None,
    event_time: Any = None,
    event_name: str = "Lead",
) -> bool:
    if not _enabled():
        return False

    phone = _normalize_phone(str(machine_data.get("phone", "")))
    tenant = str(machine_data.get("tenant", ""))
    first_name, last_name = _split_name(tenant)

    user_data: dict[str, Any] = {}
    if phone:
        user_data["ph"] = [_sha256_normalized(phone)]
    if first_name:
        user_data["fn"] = [_sha256_normalized(first_name)]
    if last_name:
        user_data["ln"] = [_sha256_normalized(last_name)]
    if lead_id is not None:
        user_data["lead_id"] = int(lead_id)

    if not user_data:
        logger.warning("Meta CAPI: no user data available for lead event")
        return False

    payload: dict[str, Any] = {
        "data": [
            {
                "event_name": event_name,
                "event_time": _to_unix_timestamp(event_time),
                "action_source": "system_generated",
                "custom_data": {
                    "event_source": "crm",
                    "lead_event_source": META_CAPI_LEAD_EVENT_SOURCE or "Telegram Bot CRM",
                },
                "user_data": user_data,
            }
        ]
    }
    if META_CAPI_TEST_EVENT_CODE:
        payload["test_event_code"] = META_CAPI_TEST_EVENT_CODE

    url = f"https://graph.facebook.com/{META_CAPI_API_VERSION}/{META_CAPI_DATASET_ID}/events"
    params = {"access_token": META_CAPI_ACCESS_TOKEN}
    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, params=params, json=payload) as resp:
                if resp.status >= 400:
                    body = await resp.text()
                    logger.warning("Meta CAPI failed: status=%s body=%s", resp.status, body)
                    return False
        return True
    except Exception:
        logger.exception("Meta CAPI request error")
        return False
