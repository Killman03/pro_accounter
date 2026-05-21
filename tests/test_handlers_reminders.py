import asyncio
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from handlers import reminders


def _machine(
    *,
    machine_id=1,
    tenant="Ivan Ivanov",
    status="active",
    rent_price=50000,
    start_date=date(2026, 1, 1),
    payments_rel=None,
):
    return SimpleNamespace(
        id=machine_id,
        tenant=tenant,
        status=status,
        rent_price=rent_price,
        start_date=start_date,
        payments_rel=payments_rel or [],
    )


def _payment(payment_date):
    return SimpleNamespace(payment_date=payment_date)


def test_last_payment_date_uses_latest_payment():
    machine = _machine(
        payments_rel=[
            _payment(date(2026, 1, 10)),
            _payment(date(2026, 2, 5)),
            _payment(date(2026, 1, 20)),
        ]
    )

    assert reminders._last_payment_date(machine) == date(2026, 2, 5)


@pytest.mark.asyncio
async def test_send_payment_reminders_sends_three_day_and_today_messages(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    machines = [
        _machine(machine_id=1, tenant="Three Days", start_date=date(2026, 1, 1)),
        _machine(machine_id=2, tenant="Today", start_date=date(2025, 12, 29)),
        _machine(machine_id=3, tenant="Later", start_date=date(2026, 1, 10)),
    ]
    monkeypatch.setattr(reminders, "get_all_machines", AsyncMock(return_value=machines))

    await reminders.send_payment_reminders(bot, chat_id=123, today=date(2026, 1, 30))

    assert bot.send_message.await_count == 2
    sent_messages = [call.args[1] for call in bot.send_message.await_args_list]
    assert "Three Days" in sent_messages[0]
    assert "через 3 дня" in sent_messages[0]
    assert "Today" in sent_messages[1]
    assert "СЕГОДНЯ" in sent_messages[1]


@pytest.mark.asyncio
async def test_send_payment_reminders_skips_inactive_machines(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    machines = [
        _machine(machine_id=1, status="closed", start_date=date(2026, 1, 4)),
    ]
    monkeypatch.setattr(reminders, "get_all_machines", AsyncMock(return_value=machines))

    await reminders.send_payment_reminders(bot, chat_id=123, today=date(2026, 2, 5))

    bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_payment_reminders_uses_last_payment_date(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    machines = [
        _machine(
            tenant="Paid User",
            start_date=date(2026, 1, 1),
            payments_rel=[_payment(date(2026, 1, 10)), _payment(date(2026, 2, 1))],
        )
    ]
    monkeypatch.setattr(reminders, "get_all_machines", AsyncMock(return_value=machines))

    await reminders.send_payment_reminders(bot, chat_id=123, today=date(2026, 3, 2))

    bot.send_message.assert_awaited_once()
    assert "Paid User" in bot.send_message.await_args.args[1]
    assert "2026-03-05" in bot.send_message.await_args.args[1]


@pytest.mark.asyncio
async def test_send_payment_reminders_continues_after_send_error(monkeypatch):
    bot = SimpleNamespace(
        send_message=AsyncMock(side_effect=[RuntimeError("telegram failed"), None])
    )
    machines = [
        _machine(machine_id=1, tenant="First", start_date=date(2026, 1, 1)),
        _machine(machine_id=2, tenant="Second", start_date=date(2026, 1, 1)),
    ]
    monkeypatch.setattr(reminders, "get_all_machines", AsyncMock(return_value=machines))

    await reminders.send_payment_reminders(bot, chat_id=123, today=date(2026, 1, 30))

    assert bot.send_message.await_count == 2


@pytest.mark.asyncio
async def test_reminders_task_sleeps_for_one_day(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(reminders, "send_payment_reminders", AsyncMock())
    sleep_mock = AsyncMock(side_effect=asyncio.CancelledError)
    monkeypatch.setattr(reminders.asyncio, "sleep", sleep_mock)

    with pytest.raises(asyncio.CancelledError):
        await reminders.reminders_task(bot, chat_id=123)

    sleep_mock.assert_awaited_once_with(24 * 60 * 60)
