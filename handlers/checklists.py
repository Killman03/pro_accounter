from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from db import add_coffee_machine, get_all_machine_models, get_all_machines
from keyboards import main_menu_kb
from utils.checklist_parser import (
    build_checklist_preview,
    looks_like_checklist,
    parse_checklist_text,
)

router = Router()


class ChecklistFSM(StatesGroup):
    waiting_text = State()
    review = State()


@router.message(Command("checklist"))
async def start_checklist(msg: Message, state: FSMContext):
    text = (msg.text or "").split(maxsplit=1)
    if len(text) == 2:
        await process_checklist_text(msg, state, text[1])
        return
    await msg.answer("Вставьте чеклист одним сообщением.", reply_markup=main_menu_kb)
    await state.set_state(ChecklistFSM.waiting_text)


@router.message(ChecklistFSM.waiting_text)
async def receive_checklist_text(msg: Message, state: FSMContext):
    await process_checklist_text(msg, state, msg.text or "")


@router.message(F.text.func(looks_like_checklist))
async def auto_receive_checklist(msg: Message, state: FSMContext):
    await process_checklist_text(msg, state, msg.text or "")


async def process_checklist_text(msg: Message, state: FSMContext, text: str):
    models = await get_all_machine_models()
    parsed = parse_checklist_text(text, models)
    issues = list(parsed.issues)
    issues.extend(await _find_duplicate_issues(parsed.values))

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Внести", callback_data="checklist_save"),
                InlineKeyboardButton(text="Отмена", callback_data="checklist_cancel"),
            ]
        ]
    )

    await state.update_data(checklist_machine=parsed.values, checklist_issues=issues)
    await msg.answer(build_checklist_preview(parsed.values, issues), reply_markup=kb)
    await state.set_state(ChecklistFSM.review)


@router.callback_query(ChecklistFSM.review, F.data == "checklist_save")
async def save_checklist(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    machine_data = data.get("checklist_machine") or {}
    issues = data.get("checklist_issues") or []

    if issues:
        await callback.message.answer(
            "Сделка не внесена. Исправьте чеклист и отправьте его заново:\n"
            + "\n".join(f"- {issue}" for issue in issues),
            reply_markup=main_menu_kb,
        )
        await callback.answer()
        return

    await add_coffee_machine(machine_data)
    await callback.message.answer("Сделка внесена из чеклиста.", reply_markup=main_menu_kb)
    await state.clear()
    await callback.answer()


@router.callback_query(ChecklistFSM.review, F.data == "checklist_cancel")
async def cancel_checklist(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Внесение чеклиста отменено.", reply_markup=main_menu_kb)
    await callback.answer()


async def _find_duplicate_issues(values: dict) -> list[str]:
    barcode = values.get("barcode")
    if not barcode:
        return []
    machines = await get_all_machines()
    duplicate = next((m for m in machines if (m.barcode or "").upper() == barcode), None)
    if not duplicate:
        return []
    return [f"Такой штрих уже есть у клиента {duplicate.tenant}"]
