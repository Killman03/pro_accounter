from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from db import get_all_machine_models, add_machine_model, delete_machine_model

router = Router()

class ModelFSM(StatesGroup):
    add_name = State()
    add_rent = State()
    add_full_price = State()

@router.message(Command("models"))
async def show_models(msg: Message, state: FSMContext):
    models = await get_all_machine_models()
    if not models:
        text = "Список моделей пуст. Добавьте новую модель."
    else:
        text = "Список моделей кофемашин:\n" + "\n".join([f"{m.id}. {m.name} (аренда: {m.default_rent})" for m in models])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить модель", callback_data="add_model")],
        *[[InlineKeyboardButton(text=f"❌ {m.name}", callback_data=f"del_model_{m.id}")] for m in models]
    ])
    await msg.answer(text, reply_markup=kb)

@router.callback_query(F.data == "add_model")
async def add_model_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название новой модели кофемашины:")
    await state.set_state(ModelFSM.add_name)
    await callback.answer()

@router.message(ModelFSM.add_name)
async def add_model_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Введите цену аренды по умолчанию для этой модели:")
    await state.set_state(ModelFSM.add_rent)

@router.message(ModelFSM.add_rent)
async def add_model_rent(msg: Message, state: FSMContext):
    try:
        rent = float(msg.text)
    except ValueError:
        await msg.answer("Введите число")
        return
    await state.update_data(default_rent=rent)
    await msg.answer("Введите полную стоимость кофемашины:")
    await state.set_state(ModelFSM.add_full_price)

@router.message(ModelFSM.add_full_price)
async def add_model_full_price(msg: Message, state: FSMContext):
    try:
        full_price = float(msg.text)
    except ValueError:
        await msg.answer("Введите число")
        return
    data = await state.get_data()
    await add_machine_model(data["name"], data["default_rent"], full_price)
    await msg.answer(f"Модель {data['name']} добавлена!")
    await state.clear()
    await show_models(msg, state)

@router.callback_query(F.data.startswith("del_model_"))
async def del_model(callback: CallbackQuery, state: FSMContext):
    model_id = int(callback.data.split("_")[-1])
    await delete_machine_model(model_id)
    await callback.message.answer("Модель удалена!")
    await show_models(callback.message, state)
    await callback.answer() 