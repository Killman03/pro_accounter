from aiogram import Router
from aiogram.types import Message
from db import get_all_machines
from datetime import date, timedelta
import asyncio

router = Router()

# Здесь будет логика автонапоминаний о платежах 

async def reminders_task(bot, chat_id):
    while True:
        machines = await get_all_machines()
        for m in machines:
            days_left = (m.payment_date - date.today()).days
            if days_left == 3:
                await bot.send_message(chat_id, f"У арендатора {m.tenant} платеж {m.rent_price} через 3 дня ({m.payment_date})")
            elif days_left == 0:
                await bot.send_message(chat_id, f"СЕГОДНЯ платеж от {m.tenant}!")
        await asyncio.sleep(24 * 60 * 60)  # Проверять раз в сутки 