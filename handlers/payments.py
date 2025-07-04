from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from db import get_all_machines, add_payment
from datetime import date, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db import AsyncSessionLocal
from models import CoffeeMachineORM
from db import get_machine_model_by_name


router = Router()

class AddPayment(StatesGroup):
    select_machine = State()
    payment_type = State()
    amount = State()
    payment_date = State()


@router.message(Command("payments"))
async def start_payments(msg: Message, state: FSMContext):
    machines = await get_all_machines()
    active_machines = [m for m in machines if m.status == "active"]

    if not active_machines:
        await msg.answer("Нет активных кофемашин для внесения платежей.")
        return

    kb_buttons = []
    for m in active_machines:
        # Получаем модель машины для получения полной цены
        machine_model = await get_machine_model_by_name(m.model)
        full_price = machine_model.full_price if machine_model else 0

        # Сумма всех платежей (исключая депозит и выкуп)
        payments_sum = sum(
            p.amount for p in m.payments_rel
            if not p.is_deposit and not p.is_buyout
        )

        # Расчет: цена - депозит - выплаты
        remaining = full_price - m.deposit - payments_sum

        kb_buttons.append(
            [InlineKeyboardButton(
                text=f"{m.tenant} - {m.model} - Остаток: {remaining:.2f}",
                callback_data=f"machine_{m.id}"
            )]
        )

    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await msg.answer("Выберите кофемашину для внесения платежа:", reply_markup=kb)
    await state.set_state(AddPayment.select_machine)

@router.callback_query(AddPayment.select_machine, F.data.startswith("machine_"))
async def select_machine_for_payment(callback: CallbackQuery, state: FSMContext):
    machine_id = int(callback.data.split("_")[1])
    await state.update_data(machine_id=machine_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Арендная плата", callback_data="type_rent")],
        [InlineKeyboardButton(text="💳 Депозит", callback_data="type_deposit")],
        [InlineKeyboardButton(text="🛒 Выкуп", callback_data="type_buyout")],
    ])
    await callback.message.answer("Выберите тип платежа:", reply_markup=kb)
    await state.set_state(AddPayment.payment_type)
    await callback.answer()

@router.callback_query(AddPayment.payment_type, F.data.startswith("type_"))
async def select_payment_type(callback: CallbackQuery, state: FSMContext):
    payment_type = callback.data.split("_")[1]
    await state.update_data(payment_type=payment_type)
    
    # Определяем сумму по умолчанию
    data = await state.get_data()
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if payment_type == "rent":
        default_amount = machine.rent_price
        await callback.message.answer(f"Введите сумму арендной платы (по умолчанию {default_amount}) или '.' для значения по умолчанию:")
    elif payment_type == "deposit":
        default_amount = machine.deposit
        await callback.message.answer(f"Введите сумму депозита (по умолчанию {default_amount}) или '.' для значения по умолчанию:")
    else:  # buyout
        await callback.message.answer("Введите сумму выкупа:")
    
    await state.set_state(AddPayment.amount)
    await callback.answer()

@router.message(AddPayment.amount)
async def input_payment_amount(msg: Message, state: FSMContext):
    if msg.text == '.':
        # Используем дефолтную сумму
        data = await state.get_data()
        machines = await get_all_machines()
        machine = next((m for m in machines if m.id == data["machine_id"]), None)
        
        if data["payment_type"] == "rent":
            amount = machine.rent_price
        elif data["payment_type"] == "deposit":
            amount = machine.deposit
        else:  # buyout
            await msg.answer("Для выкупа нужно указать конкретную сумму")
            return
        
        await state.update_data(amount=amount)
    else:
        try:
            amount = float(msg.text)
            await state.update_data(amount=amount)
        except ValueError:
            await msg.answer("Введите корректную сумму (число) или '.' для значения по умолчанию")
            return
    
    await msg.answer("Введите дату платежа (YYYY-MM-DD) или '.' (точку):")
    await state.set_state(AddPayment.payment_date)

@router.message(AddPayment.payment_date)
async def input_payment_date(msg: Message, state: FSMContext):
    try:
        if msg.text.lower() == ".":
            payment_date = date.today() + timedelta(days=0)  # Сегодняшняя дата
        else:
            payment_date = date.fromisoformat(msg.text)
    except ValueError:
        await msg.answer("Введите дату в формате YYYY-MM-DD или '.' (точку) для сегодняшней даты")
        return
    
    data = await state.get_data()
    
    # Сохраняем платеж
    payment_data = {
        "machine_id": data["machine_id"],
        "tenant": "",  # Получим из машины
        "amount": data["amount"],
        "payment_date": payment_date,
        "is_deposit": data["payment_type"] == "deposit",
        "is_buyout": data["payment_type"] == "buyout"
    }
    
    # Получаем данные машины для tenant
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    if machine:
        payment_data["tenant"] = machine.tenant
        
        # Обновляем статус машины в зависимости от типа платежа
        async with AsyncSessionLocal() as session:
            if data["payment_type"] == "buyout":
                # Выкуп - меняем статус
                await session.execute(
                    update(CoffeeMachineORM)
                    .where(CoffeeMachineORM.id == data["machine_id"])
                    .values(
                        status="buyout",
                        buyout=True,
                        buyout_date=payment_date
                    )
                )
            elif data["payment_type"] == "rent":
                # Аренда - обновляем дату следующего платежа
                next_payment = payment_date + timedelta(days=30)
                await session.execute(
                    update(CoffeeMachineORM)
                    .where(CoffeeMachineORM.id == data["machine_id"])
                    .values(payment_date=next_payment)
                )
            
            await session.commit()
    
    await add_payment(payment_data)
    
    await msg.answer(f"Платеж успешно добавлен!\n"
                    f"Тип: {data['payment_type']}\n"
                    f"Сумма: {data['amount']}\n"
                    f"Дата: {payment_date}")
    
    await state.clear() 