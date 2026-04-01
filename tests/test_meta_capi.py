import hashlib
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

import utils.meta_capi as meta_capi


class _FakeResponse:
    status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def text(self):
        return ""


class _FakeSession:
    def __init__(self, captured: dict):
        self._captured = captured

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def post(self, url, params=None, json=None, proxy=None):
        self._captured["url"] = url
        self._captured["params"] = params
        self._captured["json"] = json
        self._captured["proxy"] = proxy
        return _FakeResponse()


@pytest.mark.asyncio
async def test_send_new_user_to_meta_capi_hashes_phone_and_sets_test_event_code(monkeypatch):
    captured: dict = {}

    monkeypatch.setattr(meta_capi, "META_CAPI_ACCESS_TOKEN", "token")
    monkeypatch.setattr(meta_capi, "META_CAPI_DATASET_ID", "12345")
    monkeypatch.setattr(meta_capi, "META_CAPI_API_VERSION", "v25.0")
    monkeypatch.setattr(meta_capi, "META_CAPI_TEST_EVENT_CODE", "TEST58317")
    monkeypatch.setattr(meta_capi, "META_CAPI_PROXY_URL", "http://proxy.local:8080")
    monkeypatch.setattr(meta_capi, "send_dev_log", AsyncMock())
    monkeypatch.setattr(
        meta_capi.aiohttp,
        "ClientSession",
        lambda timeout=None, trust_env=False: _FakeSession(captured),
    )

    ok = await meta_capi.send_new_user_to_meta_capi(
        machine_data={"tenant": "Ivan Ivanov", "phone": "+996 555 123 456"},
        lead_id=101,
        event_time=datetime.now(timezone.utc),
        event_name="Lead",
    )

    assert ok is True
    assert captured["params"]["access_token"] == "token"
    assert captured["json"]["test_event_code"] == "TEST58317"
    assert captured["proxy"] == "http://proxy.local:8080"

    user_data = captured["json"]["data"][0]["user_data"]
    expected_ph = hashlib.sha256("+996555123456".encode("utf-8")).hexdigest()
    assert user_data["ph"][0] == expected_ph
