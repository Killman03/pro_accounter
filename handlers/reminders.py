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
            if m.status != "active":
                continue
            # Рассчитываем дату следующего платежа от даты начала сделки
            months_passed = (date.today() - m.start_date).days // 30
            next_payment_date = m.start_date + timedelta(days=months_passed * 30)
            days_left = (next_payment_date - date.today()).days
            if days_left == 3:
                await bot.send_message(chat_id, f"У арендатора {m.tenant} платеж {m.rent_price} через 3 дня ({next_payment_date})")
            elif days_left == 0:
                await bot.send_message(chat_id, f"СЕГОДНЯ платеж от {m.tenant}!")
        await asyncio.sleep(24 * 60 * 60)  # Проверять раз в сутки 