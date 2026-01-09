from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from db import get_all_machines, get_payments_by_machine, get_all_machine_models, get_last_payment_date
from utils.excel import generate_excel_report, generate_profit_share_report
from datetime import date, timedelta, datetime
from utils.plots import plot_top_models, plot_starts_per_day, plot_starts_per_week
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


@router.message(Command("plot_starts"))
async def plot_starts(msg: Message):
    """
    Отправляет диаграмму стартов сделок по дням выбранного месяца.
    Используется месяц первого платежа.
    Формат команды: /plot_starts YYYY-MM (например, /plot_starts 2025-09).
    Если не указано — берётся текущий месяц.
    """
    parts = msg.text.strip().split()
    if len(parts) > 1:
        try:
            dt = datetime.strptime(parts[1], "%Y-%m")
            target_month = (dt.year, dt.month)
        except ValueError:
            await msg.answer("Укажите месяц в формате YYYY-MM, например /plot_starts 2025-09")
            return
    else:
        today = date.today()
        target_month = (today.year, today.month)

    machines = await get_all_machines()
    day_counts = {}

    for m in machines:
        payments = await get_payments_by_machine(m.id)
        payments = sorted(payments, key=lambda p: p.payment_date)
        if not payments:
            continue
        first_payment = payments[0].payment_date
        if (first_payment.year, first_payment.month) != target_month:
            continue
        day = f"{first_payment.day:02d}"
        day_counts[day] = day_counts.get(day, 0) + 1

    data = [{"day": d, "count": day_counts[d]} for d in sorted(day_counts.keys())]

    if not data:
        await msg.answer("Нет данных по стартам сделок в указанном месяце.")
        return

    month_label = f"{target_month[0]:04d}-{target_month[1]:02d}"
    img = await plot_starts_per_day(data, month_label)
    img.seek(0)
    await msg.answer_photo(
        BufferedInputFile(img.read(), filename=f"starts_{month_label}.png"),
        caption=f"Старт сделок по дням ({month_label})"
    )


@router.message(Command("plot_starts_week"))
async def plot_starts_week(msg: Message):
    """
    Отправляет диаграмму стартов сделок по неделям выбранного месяца (по первому платежу).
    Формат: /plot_starts_week YYYY-MM (если не указать — текущий месяц).
    """
    parts = msg.text.strip().split()
    if len(parts) > 1:
        try:
            dt = datetime.strptime(parts[1], "%Y-%m")
            target_month = (dt.year, dt.month)
        except ValueError:
            await msg.answer("Укажите месяц в формате YYYY-MM, например /plot_starts_week 2025-09")
            return
    else:
        today = date.today()
        target_month = (today.year, today.month)

    machines = await get_all_machines()
    week_counts = {}
    week_ranges = {}

    for m in machines:
        payments = await get_payments_by_machine(m.id)
        payments = sorted(payments, key=lambda p: p.payment_date)
        if not payments:
            continue
        first_payment = payments[0].payment_date
        if (first_payment.year, first_payment.month) != target_month:
            continue
        iso_year, iso_week, _ = first_payment.isocalendar()
        week_label = f"{iso_year}-W{iso_week:02d}"
        start_of_week = first_payment - timedelta(days=first_payment.isoweekday() - 1)
        end_of_week = start_of_week + timedelta(days=6)
        week_counts[week_label] = week_counts.get(week_label, 0) + 1
        week_ranges[week_label] = (start_of_week, end_of_week)

    data = []
    for w in sorted(week_counts.keys()):
        start_of_week, end_of_week = week_ranges[w]
        label = f"{start_of_week:%d.%m}-{end_of_week:%d.%m}"
        data.append({"week": label, "count": week_counts[w]})

    if not data:
        await msg.answer("Нет данных по стартам сделок в указанном месяце.")
        return

    month_label = f"{target_month[0]:04d}-{target_month[1]:02d}"
    img = await plot_starts_per_week(data, month_label)
    img.seek(0)
    await msg.answer_photo(
        BufferedInputFile(img.read(), filename=f"starts_week_{month_label}.png"),
        caption=f"Старт сделок по неделям ({month_label})"
    )

@router.message(Command("summary"))
async def send_summary(msg: Message):
    machines = await get_all_machines()
    # Теперь просроченные платежи рассчитываются динамически от последнего платежа
    overdue = []
    for m in machines:
        if m.status != "active":
            continue
        # Получаем дату последнего платежа
        last_payment_date = await get_last_payment_date(m.id)
        if last_payment_date is None:
            last_payment_date = m.start_date
        
        # Рассчитываем дату следующего платежа
        next_payment_date = last_payment_date + timedelta(days=30)
        if next_payment_date < date.today():
            overdue.append(m)
    # Рассчитываем планируемую прибыль за месяц от активных сделок
    one_month_sum = sum(m.rent_price for m in machines if m.status == "active")
    m_act = [m for m in machines if m.status == "active"]
    text = (f"Всего кофемашин в аренде: {len(m_act)}\nПросрочено платежей: {len(overdue)}"
            f"\nСумма денег в депозитах: {sum(m.deposit for m in m_act if m.deposit)}"
            f"\nПланируемая прибыль за месяц: {one_month_sum}"
            f"\nКоличество сделок, которых нет в 1С: {sum(1 for m in m_act if not m.in_1C)}")
    await msg.answer(text) 


def _calc_rent_share(rent: float, is_first_month: bool) -> float:
    if is_first_month:
        return rent / 4
    if rent >= 10000:
        return 1500
    if rent >= 8000:
        return 1000
    return 500


def _calc_buyout_share(full_price: float) -> float:
    if full_price and full_price > 80000:
        return 2000
    if full_price and full_price > 30000:
        return 1000
    return 500


@router.message(Command("profit"))
async def send_profit_share(msg: Message):
    """
    Формирует Excel с выплатами Андрею.
    Лист = месяц старта арендатора, продолжения аренды добавляются помесячно,
    пока нет выкупа/закрытия.
    """
    machines = await get_all_machines()
    models = {m.name: m for m in await get_all_machine_models()}

    rows = []
    today_month = date.today().replace(day=1)

    for m in machines:
        payments = await get_payments_by_machine(m.id)
        payments = sorted(payments, key=lambda p: p.payment_date)
        first_payment_dt = payments[0].payment_date if payments else m.start_date
        first_month = (first_payment_dt.year, first_payment_dt.month)
        buyout_done = False
        buyout_month: tuple[int, int] | None = None
        start_month_label = first_payment_dt.strftime("%Y-%m")
        last_payment_dt = payments[-1].payment_date if payments else first_payment_dt

        # последний месяц начислений
        end_month = (today_month.year, today_month.month)
        if m.status != "active":
            end_month = (last_payment_dt.year, last_payment_dt.month)

        month_payouts: dict[str, float] = {}

        # учитываем фактические платежи (особенно выкуп)
        for p in payments:
            month_key = (p.payment_date.year, p.payment_date.month)
            month_label = p.payment_date.strftime("%Y-%m")

            if p.is_buyout:
                full_price = m.full_price if m.full_price else (models[m.model].full_price if m.model in models else 0)
                month_payouts[month_label] = month_payouts.get(month_label, 0) + _calc_buyout_share(full_price)
                buyout_done = True
                buyout_month = month_key
            elif p.is_deposit:
                continue
            else:
                if buyout_done or m.status != "active":
                    continue
                is_first_month = month_key == first_month
                month_payouts[month_label] = month_payouts.get(month_label, 0) + _calc_rent_share(m.rent_price, is_first_month)

            if p.is_buyout:
                buyout_done = True

        # продолжаем начислять аренду до текущего месяца
        # если был выкуп — только до месяца перед выкупом
        accrual_needed = True if buyout_month or (m.status == "active") or (not buyout_done) else False
        if accrual_needed:
            accrual_end = end_month
            if buyout_month:
                yb, mb = buyout_month
                accrual_end = (yb - 1, 12) if mb == 1 else (yb, mb - 1)

            y, mth = first_month
            while (y, mth) <= accrual_end:
                month_label = f"{y:04d}-{mth:02d}"
                is_first_month = (y, mth) == first_month
                if month_label not in month_payouts:
                    month_payouts[month_label] = _calc_rent_share(m.rent_price, is_first_month)
                if mth == 12:
                    y += 1
                    mth = 1
                else:
                    mth += 1

        # строка для листа месяца старта
        row_base = {
            "Месяц старта": start_month_label,
            "Дата первого платежа": first_payment_dt,
            "Дата оформления": m.start_date,
            "Арендатор": m.tenant,
            "Модель": m.model,
            "Аренда": m.rent_price,
            "Статус": m.status,
        }
        for ml, val in month_payouts.items():
            row_base[ml] = val
        rows.append(row_base)

    excel = generate_profit_share_report(rows)
    await msg.answer_document(BufferedInputFile(excel.read(), filename="profit_share.xlsx"))