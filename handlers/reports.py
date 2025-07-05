from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from db import get_all_machines, get_payments_by_machine, get_all_machine_models
from utils.excel import generate_excel_report
from utils.plots import plot_top_models
import asyncio

router = Router()

# Здесь будет логика генерации Excel-отчетов и графиков 

@router.message(Command("report"))
async def send_excel_report(msg: Message):
    machines = await get_all_machines()
    models = {m.name: m for m in await get_all_machine_models()}
    
    # Разделяем на активные и закрытые сделки
    active_machines = [m for m in machines if m.status == "active"]
    closed_machines = [m for m in machines if m.status != "active"]
    
    # Преобразуем данные для Excel - активные кофемашины
    active_machines_data = []
    payments_data = []
    closed_machines_data = []
    
    # Обрабатываем активные сделки
    for m in active_machines:
        # Получаем полную стоимость (индивидуальная или из модели)
        full_price = m.full_price if m.full_price else (models[m.model].full_price if m.model in models else 0)
        # Считаем сумму всех платежей (включая депозиты)
        all_payments = await get_payments_by_machine(m.id)
        total_paid = sum(p.amount for p in all_payments) + (m.deposit if m.deposit else 0)
        remain = full_price - total_paid
        
        active_machines_data.append({
            "Дата начала": m.start_date,
            "Арендатор": m.tenant,
            "Модель": m.model,
            "Штрих-код": m.barcode,
            "Оплата": m.rent_price,
            "Залог": m.deposit,
            "Полная стоимость": full_price,
            "Телефон": m.phone,
            "1С_статус": m.in_1C,
            "Статус": "Открыта",
            "Тип сделки": m.deal_type,
            "Комментарий": m.comment or "",
            "Остаток к выплате": remain,
        })
        
        # Платежи по активной машине
        for p in all_payments:
            remain_p = max(full_price - sum(x.amount for x in all_payments if x.payment_date <= p.payment_date), 0)
            payments_data.append({
                "Модель кофемашины": m.model,
                "Арендатор": p.tenant,
                "Сумма": p.amount,
                "Дата платежа": p.payment_date,
                "Тип": "Депозит" if p.is_deposit else ("Выкуп" if p.is_buyout else "Аренда"),
                "Остаток к доплате": remain_p,
            })
    
    # Обрабатываем закрытые сделки
    for m in closed_machines:
        # Определяем статус
        if m.status == "buyout":
            status = "Закрыта (выкуп)"
        elif m.status == "returned":
            status = "Закрыта (возврат)"
        elif m.status == "damaged":
            status = "Закрыта (повреждена)"
        else:
            status = "Закрыта"
            
        # Получаем полную стоимость
        full_price = m.full_price if m.full_price else (models[m.model].full_price if m.model in models else 0)
        # Считаем сумму всех платежей (включая депозиты)
        all_payments = await get_payments_by_machine(m.id)
        total_paid = sum(p.amount for p in all_payments)
        remain = max(full_price - total_paid, 0)
        
        closed_machines_data.append({
            "Дата начала": m.start_date,
            "Арендатор": m.tenant,
            "Модель": m.model,
            "Штрих-код": m.barcode,
            "Оплата": m.rent_price,
            "Залог": m.deposit,
            "Полная стоимость": full_price,
            "Телефон": m.phone,
            "1С_статус": m.in_1C,
            "Статус": status,
            "Тип сделки": m.deal_type,
            "Комментарий": m.comment or "",
            "Остаток к выплате": remain,
        })
        
        # Платежи по закрытой машине
        for p in all_payments:
            remain_p = max(full_price - sum(x.amount for x in all_payments if x.payment_date <= p.payment_date), 0)
            payments_data.append({
                "Модель кофемашины": m.model,
                "Арендатор": p.tenant,
                "Сумма": p.amount,
                "Дата платежа": p.payment_date,
                "Тип": "Депозит" if p.is_deposit else ("Выкуп" if p.is_buyout else "Аренда"),
                "Остаток к доплате": remain_p,
            })
    
    excel = generate_excel_report(active_machines_data, payments_data, closed_machines_data)
    excel.seek(0)
    await msg.answer_document(BufferedInputFile(excel.read(), filename="coffee_report.xlsx"))

@router.message(Command("plot"))
async def choose_plot(msg: Message):
    # Генерируем сразу график топ моделей
    machines = await get_all_machines()
    from collections import Counter
    models = [m.model for m in machines]
    counts = Counter(models)
    data = [{"model": k, "count": v} for k, v in counts.items()]
    img = await plot_top_models(data)
    
    if img:
        img.seek(0)
        await msg.answer_photo(BufferedInputFile(img.read(), filename="top_models.png"), caption="Топ моделей кофемашин")
    else:
        await msg.answer("Нет данных для построения графика")

@router.message(Command("summary"))
async def send_summary(msg: Message):
    machines = await get_all_machines()
    from datetime import date
    overdue = [m for m in machines if m.payment_date < date.today()]
    text = f"Всего кофемашин: {len(machines)}\nПросрочено платежей: {len(overdue)}"
    await msg.answer(text) 