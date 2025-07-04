from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from db import get_all_machines, get_payments_by_machine, get_all_machine_models
from utils.excel import generate_excel_report
from utils.plots import plot_payments_dynamic, plot_top_models, plot_expected_payments, plot_overdue
import asyncio

router = Router()

# Здесь будет логика генерации Excel-отчетов и графиков 

@router.message(Command("report"))
async def send_excel_report(msg: Message):
    machines = await get_all_machines()
    models = {m.name: m for m in await get_all_machine_models()}
    # Преобразуем данные для Excel - кофемашины
    machines_data = []
    payments_data = []
    for m in machines:
        # Определяем статус
        if m.status == "buyout":
            status = "Закрыта (выкуп)"
        elif m.status == "returned":
            status = "Закрыта (возврат)"
        elif m.status == "damaged":
            status = "Закрыта (повреждена)"
        else:
            status = "Открыта"
        # Получаем полную стоимость
        full_price = models[m.model].full_price if m.model in models else 0
        # Считаем сумму всех платежей
        all_payments = await get_payments_by_machine(m.id)
        total_paid = sum(p.amount for p in all_payments)
        remain = max(full_price - total_paid, 0)
        machines_data.append({
            "Дата": m.payment_date,
            "Арендатор": m.tenant,
            "Модель": m.model,
            "Штрих-код": m.barcode,
            "Оплата": m.rent_price,
            "Залог": m.deposit,
            "Телефон": m.phone,
            "1С_статус": m.in_1C,
            "Статус": status,
            "Тип сделки": m.deal_type,
            "Комментарий": m.comment or "",
            "Остаток к выплате": remain,
        })
        # Платежи по машине
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
    excel = generate_excel_report(machines_data, payments_data)
    excel.seek(0)
    await msg.answer_document(BufferedInputFile(excel.read(), filename="coffee_report.xlsx"))

@router.message(Command("plot"))
async def choose_plot(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Динамика платежей", callback_data="plot_dynamic")],
        [InlineKeyboardButton(text="🏆 Топ моделей", callback_data="plot_top")],
        [InlineKeyboardButton(text="💰 Ожидаемые платежи", callback_data="plot_expected")],
        [InlineKeyboardButton(text="⚠️ Просрочки", callback_data="plot_overdue")],
    ])
    await msg.answer("Выберите тип графика:", reply_markup=kb)

@router.callback_query(F.data.startswith("plot_"))
async def send_plot(callback: CallbackQuery):
    machines = await get_all_machines()
    if callback.data == "plot_dynamic":
        # Пример: группировка по месяцам
        from collections import Counter
        months = [m.payment_date.strftime('%Y-%m') for m in machines]
        sums = Counter(months)
        data = [{"month": k, "sum": v} for k, v in sums.items()]
        img = await plot_payments_dynamic(data)
    elif callback.data == "plot_top":
        from collections import Counter
        models = [m.model for m in machines]
        counts = Counter(models)
        data = [{"model": k, "count": v} for k, v in counts.items()]
        img = await plot_top_models(data)
    elif callback.data == "plot_expected":
        tenants = {}
        for m in machines:
            tenants[m.tenant] = tenants.get(m.tenant, 0) + m.rent_price
        data = [{"tenant": k, "sum": v} for k, v in tenants.items()]
        img = await plot_expected_payments(data)
    elif callback.data == "plot_overdue":
        # Просрочки: если дата платежа < сегодня
        from datetime import date
        overdue = []
        for m in machines:
            if m.payment_date < date.today():
                overdue.append({"tenant": m.tenant, "days": (date.today() - m.payment_date).days})
        img = await plot_overdue(overdue)
    else:
        await callback.answer("Неизвестный тип графика")
        return
    
    if img:
        img.seek(0)
        await callback.message.answer_photo(BufferedInputFile(img.read(), filename="plot.png"), caption="Ваш график")
    await callback.answer()

@router.message(Command("summary"))
async def send_summary(msg: Message):
    machines = await get_all_machines()
    from datetime import date
    overdue = [m for m in machines if m.payment_date < date.today()]
    one_month_sum = sum(m.rent_price for m in machines if m.payment_date.month == date.today().month and m.payment_date.year == date.today().year)

    m_act = [m for m in machines if m.status == "active"]
    text = (f"Всего кофемашин в аренде: {len(m_act)}\nПросрочено платежей: {len(overdue)}"
            f"\nСумма денег в депозитах: {sum(m.deposit for m in m_act if m.deposit)}"
            f"\nПланируемая прибыль за месяц: {one_month_sum}")
    await msg.answer(text) 