import asyncio
from time import perf_counter
from urllib.parse import urlsplit
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from config import BOT_TOKEN, ADMIN_ID, TELEGRAM_PROXY_URL, STARTUP_MAX_TELEGRAM_LATENCY_MS
from db import init_db
from handlers.add_machine import router as add_machine_router, start_add_machine
from handlers.reports import router as reports_router, send_excel_report, choose_plot, send_summary
from handlers.reminders import router as reminders_router, reminders_task
from handlers.payments import router as payments_router, start_payments
from handlers.models import router as models_router, show_models
from handlers.clients import router as clients_router, show_clients
from handlers.checklists import ChecklistFSM, router as checklists_router
from db import delete_coffee_machine, delete_payment, delete_coffee_machine_by_tenant, delete_payment_by_tenant

from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
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
    dp.include_router(checklists_router)


class DeleteMachineFSM(StatesGroup):
    waiting_input = State()


class DeletePaymentFSM(StatesGroup):
    waiting_input = State()


def _proxy_public_label(proxy_url: str) -> str:
    if not proxy_url:
        return "disabled"

    parsed = urlsplit(proxy_url)
    host = parsed.hostname or "unknown-host"
    port = parsed.port or "unknown-port"
    user = parsed.username or "unknown-user"
    scheme = parsed.scheme or "unknown-scheme"
    return f"{scheme}://{user}:***@{host}:{port}"


async def _send_startup_proxy_status(bot: Bot, admin_chat_id: int, proxy_url: str) -> None:
    started = perf_counter()
    await bot.get_me()
    latency_ms = int((perf_counter() - started) * 1000)
    latency_state = "OK" if latency_ms <= STARTUP_MAX_TELEGRAM_LATENCY_MS else "SLOW"
    status_text = (
        "✅ Бот запущен.\n"
        f"Proxy: {_proxy_public_label(proxy_url)}\n"
        f"Telegram API: reachable ({latency_ms} ms, {latency_state})\n"
        "Трафик aiogram направлен через указанный proxy."
    )
    await bot.send_message(admin_chat_id, status_text)
    print(status_text)


async def main():
    await init_db()

    if TELEGRAM_PROXY_URL:
        session = AiohttpSession(proxy=TELEGRAM_PROXY_URL)
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

    @dp.callback_query(F.data == "/checklist")
    async def cb_checklist(callback: CallbackQuery, state: FSMContext):
        await callback.message.answer("Вставьте чеклист одним сообщением.", reply_markup=main_menu_kb)
        await state.set_state(ChecklistFSM.waiting_text)
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
    await _send_startup_proxy_status(bot, ADMIN_CHAT_ID, TELEGRAM_PROXY_URL)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
