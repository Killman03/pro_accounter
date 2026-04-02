from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from db import get_all_machines, add_payment
from datetime import date, timedelta, datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db import AsyncSessionLocal
from models import CoffeeMachineORM
from db import get_machine_model_by_name
from db import get_all_machine_models
from db import get_payments_by_machine
from utils.meta_capi import send_new_user_to_meta_capi
from utils.meta_value import kgs_to_usd
from utils.meta_time import build_unique_meta_event_time


router = Router()


def _get_machine_full_price(machine, model_full_price: float) -> float:
    return float(machine.full_price) if machine.full_price else float(model_full_price)


def _build_meta_payment_event(
    machine,
    payment_type: str,
    payment_amount: float,
    existing_payments_count: int,
    full_price: float,
):
    # Событие только в момент оплаты, не при создании сделки.
    if machine.deal_type == "Аренда":
        if payment_type == "rent":
            value = round(payment_amount * 0.5, 2)
            return "Subscribe", value
        if payment_type == "buyout":
            value = round(full_price * 0.1, 2)
            return "Purchase", value
        return None

    if machine.deal_type == "Рассрочка":
        if existing_payments_count == 0:
            value = round(full_price * 0.1, 2)
            return "Purchase", value
        return None

    return None


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
        # Получаем модель машины для получения полной стоимости
        models = {m.name: m for m in await get_all_machine_models()}
        full_price = m.full_price if m.full_price else (models[m.model].full_price if m.model in models else 0)
        all_payments = await get_payments_by_machine(m.id)
        total_paid = sum(p.amount for p in all_payments) + (m.deposit if m.deposit else 0)

        # Расчет: цена - депозит - выплаты
        remaining = full_price - total_paid

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
        [InlineKeyboardButton(text="💳 Платеж", callback_data="type_deposit")],
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
        # Рассчитываем остаток для выкупа
        models = {m.name: m for m in await get_all_machine_models()}
        full_price = machine.full_price if machine.full_price else (models[machine.model].full_price if machine.model in models else 0)
        all_payments = await get_payments_by_machine(machine.id)
        total_paid = sum(p.amount for p in all_payments)  # Учитываем все платежи включая депозиты
        remaining = max(full_price - total_paid, 0)
        await callback.message.answer(f"Полная стоимость: {full_price}\nУже оплачено: {total_paid}\nОстаток к доплате: {remaining}\nВведите сумму выкупа:")
    
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
    
    await msg.answer("Введите дату платежа (ДД-ММ-ГГГГ или ДД.ММ.ГГГГ) либо '.' для сегодняшней даты:")
    await state.set_state(AddPayment.payment_date)

@router.message(AddPayment.payment_date)
async def input_payment_date(msg: Message, state: FSMContext):
    try:
        if msg.text.lower() == ".":
            payment_date = date.today() + timedelta(days=0)  # Сегодняшняя дата
        else:
            normalized = msg.text.replace(".", "-")
            payment_date = datetime.strptime(normalized, "%d-%m-%Y").date()
    except ValueError:
        await msg.answer("Введите дату в формате ДД-ММ-ГГГГ или ДД.ММ.ГГГГ, либо '.' для сегодняшней даты")
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
    existing_payments = []
    if machine:
        payment_data["tenant"] = machine.tenant
        existing_payments = await get_payments_by_machine(machine.id)
        
        # Обновляем статус машины в зависимости от типа платежа
        async with AsyncSessionLocal() as session:
            if machine.deal_type == "Рассрочка" and len(existing_payments) == 0:
                await session.execute(
                    update(CoffeeMachineORM)
                    .where(CoffeeMachineORM.id == data["machine_id"])
                    .values(start_date=payment_date)
                )
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

            
            await session.commit()
    
    await add_payment(payment_data)
    if machine:
        models = {m.name: m for m in await get_all_machine_models()}
        model_full_price = models[machine.model].full_price if machine.model in models else 0
        full_price = _get_machine_full_price(machine, model_full_price)
        event_payload = _build_meta_payment_event(
            machine=machine,
            payment_type=data["payment_type"],
            payment_amount=float(data["amount"]),
            existing_payments_count=len(existing_payments),
            full_price=full_price,
        )
        if event_payload is not None:
            event_name, event_value = event_payload
            meta_event_time = build_unique_meta_event_time(payment_date)
            await send_new_user_to_meta_capi(
                {"tenant": machine.tenant, "phone": machine.phone},
                lead_id=machine.id,
                event_time=meta_event_time,
                event_name=event_name,
                custom_data={
                    "value": kgs_to_usd(event_value),
                    "currency": "USD",
                    "payment_type": data["payment_type"],
                },
            )
    
    await msg.answer(f"Платеж успешно добавлен!\n"
                    f"Тип: {data['payment_type']}\n"
                    f"Сумма: {data['amount']}\n"
                    f"Дата: {payment_date}")
    
    await state.clear() 
