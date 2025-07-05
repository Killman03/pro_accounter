from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from db import add_coffee_machine, get_all_machine_models
from utils.models_list import MODELS
from utils.validators import validate_kg_phone
from datetime import date, timedelta
from keyboards import main_menu_kb

router = Router()

class AddMachine(StatesGroup):
    model = State()
    barcode = State()
    rent_price = State()
    tenant = State()
    phone = State()
    deposit = State()
    in_1C = State()
    deal_type = State()
    comment = State()

@router.message(Command("add_machine"))
async def start_add_machine(msg: Message, state: FSMContext):
    models = await get_all_machine_models()
    if not models:
        await msg.answer("Нет доступных моделей. Добавьте их через /models", reply_markup=main_menu_kb)
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=m.name, callback_data=f"model_{m.id}")] for m in models]
    )
    await msg.answer("Выберите модель кофемашины:", reply_markup=kb)
    await state.set_state(AddMachine.model)

@router.callback_query(AddMachine.model, F.data.startswith("model_"))
async def select_model(callback: CallbackQuery, state: FSMContext):
    model_id = int(callback.data.split("_")[1])
    models = await get_all_machine_models()
    model = next((m for m in models if m.id == model_id), None)
    if not model:
        await callback.message.answer("Модель не найдена", reply_markup=main_menu_kb)
        await callback.answer()
        return
    await state.update_data(model=model.name, rent_price=model.default_rent)
    await callback.message.answer(f"Вы выбрали: {model.name}. Введите штрих-код:", reply_markup=main_menu_kb)
    await state.set_state(AddMachine.barcode)
    await callback.answer()

@router.message(AddMachine.barcode)
async def input_barcode(msg: Message, state: FSMContext):
    await state.update_data(barcode=msg.text)
    data = await state.get_data()
    await msg.answer(f"Цена аренды по умолчанию: {data['rent_price']}\nЕсли хотите изменить, введите новую цену, иначе напишите '.' (точку) для сохранения по умолчанию.", reply_markup=main_menu_kb)
    await state.set_state(AddMachine.rent_price)

@router.message(AddMachine.rent_price)
async def input_rent_price(msg: Message, state: FSMContext):
    if msg.text != '.':
        try:
            rent_price = float(msg.text)
            await state.update_data(rent_price=rent_price)
        except ValueError:
            await msg.answer("Введите число или '.' для значения по умолчанию", reply_markup=main_menu_kb)
            return
    await msg.answer("Введите ФИО арендатора:", reply_markup=main_menu_kb)
    await state.set_state(AddMachine.tenant)

@router.message(AddMachine.tenant)
async def input_tenant(msg: Message, state: FSMContext):
    await state.update_data(tenant=msg.text)
    await msg.answer("Введите телефон арендатора (996XXXXXXXXX):", reply_markup=main_menu_kb)
    await state.set_state(AddMachine.phone)

@router.message(AddMachine.phone)
async def input_phone(msg: Message, state: FSMContext):
    if not validate_kg_phone(msg.text):
        await msg.answer("Телефон должен быть в формате 996XXXXXXXXX", reply_markup=main_menu_kb)
        return
    await state.update_data(phone=msg.text)
    await msg.answer("Введите сумму залога:", reply_markup=main_menu_kb)
    await state.set_state(AddMachine.deposit)

@router.message(AddMachine.deposit)
async def input_deposit(msg: Message, state: FSMContext):
    try:
        deposit = float(msg.text)
        await state.update_data(deposit=deposit)
    except ValueError:
        await msg.answer("Введите число", reply_markup=main_menu_kb)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В 1С", callback_data="in1c_true"), InlineKeyboardButton(text="Без 1С", callback_data="in1c_false")]
    ])
    await msg.answer("Добавить отметку о 1С?", reply_markup=kb)
    await state.set_state(AddMachine.in_1C)



@router.callback_query(AddMachine.in_1C)
async def input_in1c(callback: CallbackQuery, state: FSMContext):
    in_1C = callback.data == "in1c_true"
    await state.update_data(in_1C=in_1C)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Аренда", callback_data="dealtype_rent"), InlineKeyboardButton(text="Рассрочка", callback_data="dealtype_installment")]
    ])
    await callback.message.answer("Выберите тип сделки:", reply_markup=kb)
    await state.set_state(AddMachine.deal_type)
    await callback.answer()

@router.callback_query(AddMachine.deal_type)
async def input_deal_type(callback: CallbackQuery, state: FSMContext):
    deal_type = "Аренда" if callback.data == "dealtype_rent" else "Рассрочка"
    await state.update_data(deal_type=deal_type)
    await callback.message.answer("Введите комментарий (или '-' если не требуется):")
    await state.set_state(AddMachine.comment)
    await callback.answer()

@router.message(AddMachine.comment)
async def input_comment(msg: Message, state: FSMContext):
    comment = None if msg.text.strip() == '-' else msg.text.strip()
    await state.update_data(comment=comment)
    data = await state.get_data()
    await add_coffee_machine({
        "model": data["model"],
        "barcode": data["barcode"],
        "rent_price": data["rent_price"],
        "tenant": data["tenant"],
        "phone": data["phone"],
        "deposit": data["deposit"],
        "start_date": date.today(),
        "in_1C": data["in_1C"],
        "status": "active",
        "buyout": False,
        "buyout_date": None,
        "payments": [],
        "deal_type": data["deal_type"],
        "comment": data["comment"]
    })
    await msg.answer("Кофемашина успешно добавлена!")
    await state.clear() 