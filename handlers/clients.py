from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from db import get_all_machines, update_machine_full_price, update_machine_deal_type, update_machine_1c, update_machine_rent_price, get_payments_by_machine, get_all_machine_models, get_last_payment_date
from datetime import date, timedelta

router = Router()

async def get_client_info(machine):
    """Получает подробную информацию о клиенте"""
    # Получаем модель машины для полной стоимости
    models = {m.name: m for m in await get_all_machine_models()}
    full_price = machine.full_price if machine.full_price else (models[machine.model].full_price if machine.model in models else 0)
    
    # Получаем все платежи
    all_payments = await get_payments_by_machine(machine.id)
    total_paid = sum(p.amount for p in all_payments) + (machine.deposit if machine.deposit else 0)
    remaining = max(full_price - total_paid, 0)
    
    # Получаем дату последнего платежа
    last_payment_date = await get_last_payment_date(machine.id)
    if last_payment_date is None:
        last_payment_date = machine.start_date
    
    # Рассчитываем дату следующего платежа
    next_payment_date = last_payment_date + timedelta(days=32)
    days_left = (next_payment_date - date.today()).days
    
    # Статус платежа
    if days_left < 0:
        payment_status = f"🔴 ПРОШЛА ({abs(days_left)} дн. назад)"
    elif days_left == 0:
        payment_status = "🔴 СЕГОДНЯ ПЛАТЕЖ!"
    elif days_left <= 3:
        payment_status = f"🟡 Через {days_left} дня"
    elif days_left <= 7:
        payment_status = f"🟠 Через {days_left} дней"
    else:
        payment_status = f"🟢 Через {days_left} дней"
    
    info = f"👤 **{machine.tenant}**\n"
    info += f"📱 Телефон: {machine.phone}\n"
    info += f"☕️ Модель: {machine.model}\n"
    info += f"📅 Дата начала: {machine.start_date}\n"
    info += f"💰 Аренда: {machine.rent_price}\n"
    info += f"💳 Депозит: {machine.deposit}\n"
    info += f"💵 Полная стоимость кофемашины: {full_price}\n"
    info += f"📊 Тип сделки: {machine.deal_type}\n"
    info += f"🏢 1С статус: {'✅ В 1С' if machine.in_1C else '❌ Без 1С'}\n"
    info += f"💸 Уже оплачено с депозитом: {total_paid}\n"
    info += f"⚖️ Остаток: {remaining}\n"
    info += f"📅 Последний платеж: {last_payment_date}\n"
    info += f"⏰ Следующий платеж: {next_payment_date}\n"
    info += f"📊 Статус: {payment_status}\n"
    
    if machine.comment:
        info += f"💬 Комментарий: {machine.comment}\n"
    
    return info

class EditFSM(StatesGroup):
    select_machine = State()
    action = State()
    new_price = State()
    new_deal_type = State()
    new_1c = State()
    new_rent = State()

@router.message(Command("clients"))
async def show_clients(msg: Message, state: FSMContext):
    machines = await get_all_machines()
    active_machines = [m for m in machines if m.status == "active"]
    
    if not active_machines:
        await msg.answer("📋 Нет активных клиентов")
        return
    
    # Создаем кнопки с более подробной информацией
    kb_buttons = []
    for m in active_machines:
        # Получаем информацию о платежах
        all_payments = await get_payments_by_machine(m.id)
        total_paid = sum(p.amount for p in all_payments) + (m.deposit if m.deposit else 0)
        
        # Получаем дату последнего платежа
        last_payment_date = await get_last_payment_date(m.id)
        if last_payment_date is None:
            last_payment_date = m.start_date
        
        # Рассчитываем дату следующего платежа
        next_payment_date = last_payment_date + timedelta(days=32)
        days_left = (next_payment_date - date.today()).days
        
        # Статус платежа
        if days_left < 0:
            payment_status = f"🔴 ПРОШЛА"
        elif days_left == 0:
            payment_status = f"🔴 СЕГОДНЯ"
        elif days_left <= 3:
            payment_status = f"🟡 {days_left}д"
        elif days_left <= 7:
            payment_status = f"🟠 {days_left}д"
        else:
            payment_status = f"🟢 {days_left}д"
        
        button_text = f"{m.tenant} | {m.model} | {payment_status} | {m.rent_price}₸"
        kb_buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"client_{m.id}")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    summary_text = f"📋 **Активные клиенты ({len(active_machines)})**\n\n"
    summary_text += f"🔴 ПРОШЛА - платеж просрочен\n"
    summary_text += f"🔴 СЕГОДНЯ - платеж сегодня\n"
    summary_text += f"🟡 Xд - платеж через X дней (срочно)\n"
    summary_text += f"🟠 Xд - платеж через X дней (внимание)\n"
    summary_text += f"🟢 Xд - платеж через X дней (нормально)\n\n"
    summary_text += f"Выберите клиента для просмотра подробной информации:"
    
    await msg.answer(summary_text, reply_markup=kb)
    await state.set_state(EditFSM.select_machine)

@router.callback_query(EditFSM.select_machine, F.data.startswith("client_"))
async def select_client(callback: CallbackQuery, state: FSMContext):
    machine_id = int(callback.data.split("_")[1])
    
    # Получаем информацию о машине
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == machine_id), None)
    
    if not machine:
        await callback.message.answer("Клиент не найден!")
        await callback.answer()
        return
    
    # Показываем текущую информацию о клиенте
    client_info = await get_client_info(machine)
    await callback.message.answer(f"📋 **Текущая информация о клиенте:**\n\n{client_info}")
    
    await state.update_data(machine_id=machine_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Изменить стоимость", callback_data="edit_price")],
        [InlineKeyboardButton(text="📊 Изменить тип сделки", callback_data="edit_dealtype")],
        [InlineKeyboardButton(text="🏢 Изменить 1С статус", callback_data="edit_1c")],
        [InlineKeyboardButton(text="💵 Изменить аренду", callback_data="edit_rent")],
    ])
    await callback.message.answer("Выберите действие для изменения:", reply_markup=kb)
    await state.set_state(EditFSM.action)
    await callback.answer()

@router.callback_query(EditFSM.action, F.data == "edit_price")
async def edit_price_start(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if machine:
        current_price = machine.full_price if machine.full_price else "Не установлена"
        await callback.message.answer(f"💰 **Изменение стоимости кофемашины**\n\n"
                                    f"👤 Клиент: {machine.tenant}\n"
                                    f"☕️ Модель: {machine.model}\n"
                                    f"💵 Текущая стоимость: {current_price}\n\n"
                                    f"Введите новую стоимость:")
    else:
        await callback.message.answer("Клиент не найден!")
    
    await state.set_state(EditFSM.new_price)
    await callback.answer()

@router.message(EditFSM.new_price)
async def edit_price_save(msg: Message, state: FSMContext):
    try:
        price = float(msg.text)
    except ValueError:
        await msg.answer("Введите число")
        return
    
    data = await state.get_data()
    await update_machine_full_price(data["machine_id"], price)
    
    # Показываем обновленную информацию
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if machine:
        await msg.answer(f"✅ **Стоимость успешно обновлена!**\n\n"
                        f"👤 Клиент: {machine.tenant}\n"
                        f"💵 Новая стоимость: {price}\n\n"
                        f"📋 Обновленная информация:")
        client_info = await get_client_info(machine)
        await msg.answer(client_info)
    else:
        await msg.answer("✅ Стоимость обновлена!")
    
    await state.clear()

@router.callback_query(EditFSM.action, F.data == "edit_dealtype")
async def edit_dealtype_start(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if machine:
        await callback.message.answer(f"📊 **Изменение типа сделки**\n\n"
                                    f"👤 Клиент: {machine.tenant}\n"
                                    f"☕️ Модель: {machine.model}\n"
                                    f"📊 Текущий тип: {machine.deal_type}\n\n"
                                    f"Выберите новый тип сделки:")
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Аренда", callback_data="dealtype_rent"), InlineKeyboardButton(text="Рассрочка", callback_data="dealtype_installment")]
        ])
        await callback.message.answer("Выберите новый тип сделки:", reply_markup=kb)
    else:
        await callback.message.answer("Клиент не найден!")
    
    await state.set_state(EditFSM.new_deal_type)
    await callback.answer()

@router.callback_query(EditFSM.new_deal_type)
async def edit_dealtype_save(callback: CallbackQuery, state: FSMContext):
    new_type = "Аренда" if callback.data == "dealtype_rent" else "Рассрочка"
    data = await state.get_data()
    await update_machine_deal_type(data["machine_id"], new_type)
    
    # Показываем обновленную информацию
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if machine:
        await callback.message.answer(f"✅ **Тип сделки успешно обновлен!**\n\n"
                                    f"👤 Клиент: {machine.tenant}\n"
                                    f"📊 Новый тип: {new_type}\n\n"
                                    f"📋 Обновленная информация:")
        client_info = await get_client_info(machine)
        await callback.message.answer(client_info)
    else:
        await callback.message.answer("✅ Тип сделки обновлен!")
    
    await state.clear()
    await callback.answer()

@router.callback_query(EditFSM.action, F.data == "edit_1c")
async def edit_1c_start(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if machine:
        current_1c = "✅ В 1С" if machine.in_1C else "❌ Без 1С"
        await callback.message.answer(f"🏢 **Изменение статуса 1С**\n\n"
                                    f"👤 Клиент: {machine.tenant}\n"
                                    f"☕️ Модель: {machine.model}\n"
                                    f"🏢 Текущий статус: {current_1c}\n\n"
                                    f"Выберите новый статус 1С:")
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ В 1С", callback_data="1c_true"), InlineKeyboardButton(text="❌ Без 1С", callback_data="1c_false")]
        ])
        await callback.message.answer("Выберите новый статус 1С:", reply_markup=kb)
    else:
        await callback.message.answer("Клиент не найден!")
    
    await state.set_state(EditFSM.new_1c)
    await callback.answer()

@router.callback_query(EditFSM.new_1c)
async def edit_1c_save(callback: CallbackQuery, state: FSMContext):
    new_1c = callback.data == "1c_true"
    data = await state.get_data()
    await update_machine_1c(data["machine_id"], new_1c)
    
    # Показываем обновленную информацию
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if machine:
        new_1c_text = "✅ В 1С" if new_1c else "❌ Без 1С"
        await callback.message.answer(f"✅ **Статус 1С успешно обновлен!**\n\n"
                                    f"👤 Клиент: {machine.tenant}\n"
                                    f"🏢 Новый статус: {new_1c_text}\n\n"
                                    f"📋 Обновленная информация:")
        client_info = await get_client_info(machine)
        await callback.message.answer(client_info)
    else:
        await callback.message.answer("✅ Статус 1С обновлен!")
    
    await state.clear()
    await callback.answer()

@router.callback_query(EditFSM.action, F.data == "edit_rent")
async def edit_rent_start(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if machine:
        await callback.message.answer(f"💵 **Изменение суммы аренды**\n\n"
                                    f"👤 Клиент: {machine.tenant}\n"
                                    f"☕️ Модель: {machine.model}\n"
                                    f"💰 Текущая аренда: {machine.rent_price}\n\n"
                                    f"Введите новую сумму аренды:")
    else:
        await callback.message.answer("Клиент не найден!")
    
    await state.set_state(EditFSM.new_rent)
    await callback.answer()

@router.message(EditFSM.new_rent)
async def edit_rent_save(msg: Message, state: FSMContext):
    try:
        rent = float(msg.text)
    except ValueError:
        await msg.answer("Введите число")
        return
    
    data = await state.get_data()
    await update_machine_rent_price(data["machine_id"], rent)
    
    # Показываем обновленную информацию
    machines = await get_all_machines()
    machine = next((m for m in machines if m.id == data["machine_id"]), None)
    
    if machine:
        await msg.answer(f"✅ **Сумма аренды успешно обновлена!**\n\n"
                        f"👤 Клиент: {machine.tenant}\n"
                        f"💰 Новая аренда: {rent}\n\n"
                        f"📋 Обновленная информация:")
        client_info = await get_client_info(machine)
        await msg.answer(client_info)
    else:
        await msg.answer("✅ Аренда обновлена!")
    
    await state.clear() 