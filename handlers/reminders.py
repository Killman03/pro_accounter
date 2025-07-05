from aiogram import Router
from aiogram.types import Message
from db import get_all_machines, get_last_payment_date
from datetime import date, timedelta
import asyncio

router = Router()

# Здесь будет логика автонапоминаний о платежах 

async def reminders_task(bot, chat_id):
    while True:
        machines = await get_all_machines()
        for machine in machines:
            if str(machine.status) != "active":
                continue
            
            # Получаем дату последнего платежа
            last_payment_date = await get_last_payment_date(machine.id)
            
            # Если платежей нет, используем дату начала сделки
            if last_payment_date is None:
                last_payment_date = machine.start_date
            
            # Рассчитываем дату следующего платежа от последнего платежа
            next_payment_date = last_payment_date + timedelta(days=32)
            days_left = (next_payment_date - date.today()).days
            
            if days_left == 3:
                await bot.send_message(chat_id, f"У арендатора {machine.tenant} платеж {machine.rent_price} через 3 дня ({next_payment_date})")
            elif days_left == 0:
                await bot.send_message(chat_id, f"СЕГОДНЯ платеж от {machine.tenant}!")
        await asyncio.sleep(24 * 24 * 60)  # Проверять раз в сутки