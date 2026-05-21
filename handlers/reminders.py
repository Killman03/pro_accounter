import asyncio
import logging
from datetime import date, timedelta

from aiogram import Router

from db import get_all_machines

router = Router()
logger = logging.getLogger(__name__)

REMINDER_INTERVAL_SECONDS = 24 * 60 * 60


def _last_payment_date(machine):
    payments = machine.payments_rel or []
    if not payments:
        return None
    return max(p.payment_date for p in payments)


def _payment_reminder_message(machine, today):
    last_payment_date = _last_payment_date(machine)
    if last_payment_date is None:
        last_payment_date = machine.start_date

    next_payment_date = last_payment_date + timedelta(days=32)
    days_left = (next_payment_date - today).days

    if days_left == 3:
        return (
            f"У арендатора {machine.tenant} платеж {machine.rent_price} "
            f"через 3 дня ({next_payment_date})"
        )
    if days_left == 0:
        return f"СЕГОДНЯ платеж от {machine.tenant}!"
    return None


async def send_payment_reminders(bot, chat_id, today=None):
    today = today or date.today()
    machines = await get_all_machines()

    for machine in machines:
        if str(machine.status) != "active":
            continue

        message = _payment_reminder_message(machine, today)
        if message is None:
            continue

        try:
            await bot.send_message(chat_id, message)
        except Exception:
            logger.exception(
                "Failed to send payment reminder: machine_id=%s tenant=%s",
                getattr(machine, "id", None),
                getattr(machine, "tenant", None),
            )


async def reminders_task(bot, chat_id):
    while True:
        try:
            await send_payment_reminders(bot, chat_id)
        except Exception:
            logger.exception("Payment reminders task iteration failed")
        await asyncio.sleep(REMINDER_INTERVAL_SECONDS)
