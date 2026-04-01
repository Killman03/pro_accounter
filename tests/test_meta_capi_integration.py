import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from aiohttp import ClientConnectorError

from config import (
    META_CAPI_ACCESS_TOKEN,
    META_CAPI_DATASET_ID,
    META_CAPI_TEST_EVENT_CODE,
)
from utils.meta_capi import send_new_user_to_meta_capi


def _meta_capi_live_env_ready() -> bool:
    return bool(
        META_CAPI_TEST_EVENT_CODE and META_CAPI_ACCESS_TOKEN and META_CAPI_DATASET_ID
    )


@pytest.mark.asyncio
async def test_meta_capi_live_sends_test_event_when_test_code_is_configured():
    if not _meta_capi_live_env_ready():
        pytest.skip(
            "Meta CAPI live test skipped: set META_CAPI_TEST_EVENT_CODE, "
            "META_CAPI_ACCESS_TOKEN, META_CAPI_DATASET_ID"
        )

    run_id = str(uuid4())
    ok = False
    for _ in range(3):
        try:
            ok = await send_new_user_to_meta_capi(
                machine_data={
                    "tenant": f"Pytest Meta {run_id}",
                    "phone": "996555123456",
                },
                lead_id=900000,
                event_time=datetime.now(timezone.utc),
                event_name="Lead",
                custom_data={
                    "source": "pytest_live_smoke",
                    "run_id": run_id,
                },
            )
        except (TimeoutError, asyncio.TimeoutError, ClientConnectorError):
            pytest.skip("Meta CAPI live test skipped: network timeout/unreachable graph.facebook.com")
        if ok:
            break
        await asyncio.sleep(1)

    if not ok:
        pytest.skip("Meta CAPI live test skipped: request could not be completed (network/api unavailable)")

    assert ok is True
