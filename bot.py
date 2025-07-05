import asyncio
from aiogram import Bot, Dispatcher, F
from config import BOT_TOKEN, ADMIN_ID
from db import init_db
from handlers.add_machine import router as add_machine_router, start_add_machine
from handlers.reports import router as reports_router, send_excel_report, choose_plot, send_summary
from handlers.reminders import router as reminders_router, reminders_task
from handlers.payments import router as payments_router, start_payments
from handlers.models import router as models_router, show_models
from handlers.clients import router as clients_router, show_clients

from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from keyboards import main_menu_kb

# Укажите свой chat_id для напоминаний
ADMIN_CHAT_ID = ADMIN_ID

def setup_routers(dp: Dispatcher):
    dp.include_router(add_machine_router)
    dp.include_router(reports_router)
    dp.include_router(reminders_router)
    dp.include_router(payments_router)
    dp.include_router(models_router)
    dp.include_router(clients_router)

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    setup_routers(dp)

    @dp.message(Command("start"))
    async def start_cmd(msg: Message):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="☕️ Добавить сделку", callback_data="/add_machine")],
            [InlineKeyboardButton(text="💳 Платежи", callback_data="/payments")],
            [InlineKeyboardButton(text="💎 Модели кофемашин", callback_data="/models")],
            [InlineKeyboardButton(text="👨‍🦰 Мои арендаторы", callback_data="/clients")],
            [InlineKeyboardButton(text="📑 Отчет (Excel)", callback_data="/report")],
            [InlineKeyboardButton(text="📈 Графики", callback_data="/plot")],
            [InlineKeyboardButton(text="🌡 Выжимка", callback_data="/summary")],
        ])
        await msg.answer("Добро пожаловать! Выберите действие:", reply_markup=kb)

    @dp.callback_query(F.data == "/add_machine")
    async def cb_add_machine(callback: CallbackQuery, state: FSMContext):
        await start_add_machine(callback.message, state)
        await callback.answer()

    @dp.callback_query(F.data == "/payments")
    async def cb_payments(callback: CallbackQuery, state: FSMContext):
        await start_payments(callback.message, state)
        await callback.answer()

    @dp.callback_query(F.data == "/models")
    async def cb_models(callback: CallbackQuery, state: FSMContext):
        await show_models(callback.message, state)
        await callback.answer()

    @dp.callback_query(F.data == "/report")
    async def cb_report(callback: CallbackQuery):
        await send_excel_report(callback.message)
        await callback.answer()

    @dp.callback_query(F.data == "/plot")
    async def cb_plot(callback: CallbackQuery):
        await choose_plot(callback.message)
        await callback.answer()

    @dp.callback_query(F.data == "/summary")
    async def cb_summary(callback: CallbackQuery):
        await send_summary(callback.message)
        await callback.answer()

    @dp.callback_query(F.data == "/clients")
    async def cb_clients(callback: CallbackQuery, state: FSMContext):
        await show_clients(callback.message, state)
        await callback.answer()

    # Запуск автонапоминаний в фоне
    asyncio.create_task(reminders_task(bot, ADMIN_CHAT_ID))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 