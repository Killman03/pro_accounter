import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from config import BOT_TOKEN, ADMIN_ID, TG_PROXY, TG_PROXY_URL
from db import init_db
from handlers.add_machine import router as add_machine_router, start_add_machine
from handlers.reports import router as reports_router, send_excel_report, choose_plot, send_summary
from handlers.reminders import router as reminders_router, reminders_task
from handlers.payments import router as payments_router, start_payments
from handlers.models import router as models_router, show_models
from handlers.clients import router as clients_router, show_clients
from db import delete_coffee_machine, delete_payment, delete_coffee_machine_by_tenant, delete_payment_by_tenant

from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import main_menu_kb
from urllib.parse import quote

# Укажите свой chat_id для напоминаний
ADMIN_CHAT_ID = ADMIN_ID

def setup_routers(dp: Dispatcher):
    dp.include_router(add_machine_router)
    dp.include_router(reports_router)
    dp.include_router(reminders_router)
    dp.include_router(payments_router)
    dp.include_router(models_router)
    dp.include_router(clients_router)


class DeleteMachineFSM(StatesGroup):
    waiting_input = State()


class DeletePaymentFSM(StatesGroup):
    waiting_input = State()


def _build_proxy_url(proxy_value: str) -> str:
    value = (proxy_value or "").strip()
    if not value:
        return ""

    if "://" in value:
        return value

    parts = value.split(":")
    if len(parts) == 2:
        host, port = parts
        return f"socks5://{host}:{port}"

    if len(parts) == 4:
        host, port, username, password = parts
        user_enc = quote(username, safe="")
        pass_enc = quote(password, safe="")
        return f"socks5://{user_enc}:{pass_enc}@{host}:{port}"

    raise ValueError(
        "Invalid proxy format. Use TG_PROXY=host:port:username:password "
        "or TG_PROXY=host:port"
    )


async def main():
    await init_db()
    proxy_value = TG_PROXY or TG_PROXY_URL
    proxy_url = _build_proxy_url(proxy_value) if proxy_value else ""

    if proxy_url:
        session = AiohttpSession(proxy=proxy_url)
        bot = Bot(token=BOT_TOKEN, session=session)
    else:
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
        # Отдельно показываем обычную клавиатуру с быстрыми командами (в т.ч. /profit)
        await msg.answer("Быстрые команды:", reply_markup=main_menu_kb)

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

    @dp.message(Command("delete_machine"))
    async def delete_machine_cmd(msg: Message, state: FSMContext):
        parts = msg.text.strip().split(maxsplit=1)
        if len(parts) == 2:
            await _process_delete_machine(msg, parts[1].strip())
            return
        await msg.answer("Введите ID сделки или ФИО арендатора для удаления сделки:")
        await state.set_state(DeleteMachineFSM.waiting_input)

    @dp.message(DeleteMachineFSM.waiting_input)
    async def delete_machine_wait(msg: Message, state: FSMContext):
        await _process_delete_machine(msg, msg.text.strip())
        await state.clear()

    async def _process_delete_machine(msg: Message, arg: str):
        if arg.isdigit():
            machine_id = int(arg)
            await delete_coffee_machine(machine_id)
            await msg.answer(f"Сделка (машина) с id={machine_id} удалена.")
        else:
            deleted = await delete_coffee_machine_by_tenant(arg)
            if deleted:
                await msg.answer(f"Удалено сделок: {deleted} по арендатору '{arg}'.")
            else:
                await msg.answer(f"Сделки с арендатором '{arg}' не найдены.")

    @dp.message(Command("delete_payment"))
    async def delete_payment_cmd(msg: Message, state: FSMContext):
        parts = msg.text.strip().split(maxsplit=1)
        if len(parts) == 2:
            arg = parts[1].strip()
            await _process_delete_payment(msg, arg)
            return
        await msg.answer("Введите ID платежа или ФИО арендатора для удаления платежей:")
        await state.set_state(DeletePaymentFSM.waiting_input)

    @dp.message(DeletePaymentFSM.waiting_input)
    async def delete_payment_wait(msg: Message, state: FSMContext):
        arg = msg.text.strip()
        await _process_delete_payment(msg, arg)
        await state.clear()

    async def _process_delete_payment(msg: Message, arg: str):
        if arg.isdigit():
            payment_id = int(arg)
            await delete_payment(payment_id)
            await msg.answer(f"Платеж с id={payment_id} удален.")
        else:
            deleted = await delete_payment_by_tenant(arg)
            if deleted:
                await msg.answer(f"Удалено платежей: {deleted} по арендатору '{arg}'.")
            else:
                await msg.answer(f"Платежи по арендатору '{arg}' не найдены.")

    # Запуск автонапоминаний в фоне
    asyncio.create_task(reminders_task(bot, ADMIN_CHAT_ID))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
