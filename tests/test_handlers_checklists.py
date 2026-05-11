from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.checklists import ChecklistFSM, process_checklist_text, save_checklist


@pytest.mark.asyncio
async def test_process_checklist_text_builds_review_without_issues():
    msg = AsyncMock(spec=Message)
    msg.text = "Чек лист"
    msg.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    models = [SimpleNamespace(name="SES 880")]
    text = """[25.04.2026 12:22] Ивасик: Чек лист
ФИО Камчибекова А
Модель ses 880
Штрих: SAGE254SJ32CE
Цена 55000
Аренда 5000
Депозит 5000
Телефон: 0502280928
Дата первой оплаты сегодня"""

    with (
        patch("handlers.checklists.get_all_machine_models", new_callable=AsyncMock, return_value=models),
        patch("handlers.checklists.get_all_machines", new_callable=AsyncMock, return_value=[]),
    ):
        await process_checklist_text(msg, state, text)

    state.update_data.assert_called_once()
    saved = state.update_data.call_args.kwargs["checklist_machine"]
    assert saved["tenant"] == "Камчибекова А"
    assert saved["phone"] == "996502280928"
    assert saved["start_date"] == date(2026, 4, 25)
    assert state.update_data.call_args.kwargs["checklist_issues"] == []
    state.set_state.assert_called_once_with(ChecklistFSM.review)
    msg.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_checklist_text_reports_duplicate_barcode():
    msg = AsyncMock(spec=Message)
    msg.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    models = [SimpleNamespace(name="SES 990")]
    machines = [SimpleNamespace(barcode="A1SGFESA211900038", tenant="Абдурахмнова Наргиза")]
    text = """[11.05.2026 15:19] Ивасик: Чек лист
ФИО Озорбаев Иса
Модель ses 990
Штрих A1SGFESA211900038
Цена 110000
Аренда 10000
Депозит 15000
Телефон: 0707554449
Дата первой оплаты - сегодня"""

    with (
        patch("handlers.checklists.get_all_machine_models", new_callable=AsyncMock, return_value=models),
        patch("handlers.checklists.get_all_machines", new_callable=AsyncMock, return_value=machines),
    ):
        await process_checklist_text(msg, state, text)

    issues = state.update_data.call_args.kwargs["checklist_issues"]
    assert issues == ["Такой штрих уже есть у клиента Абдурахмнова Наргиза"]


@pytest.mark.asyncio
async def test_save_checklist_writes_machine_when_no_issues():
    callback = AsyncMock(spec=CallbackQuery)
    callback.message = AsyncMock(spec=Message)
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    machine_data = {
        "model": "SES 880",
        "barcode": "SAGE254SJ32CE",
        "rent_price": 5000.0,
        "tenant": "Камчибекова А",
        "phone": "996502280928",
        "deposit": 5000.0,
        "start_date": date(2026, 4, 25),
        "in_1C": False,
        "status": "active",
        "buyout": False,
        "buyout_date": None,
        "payments": [],
        "deal_type": "Аренда",
        "comment": None,
        "full_price": 55000.0,
    }
    state.get_data = AsyncMock(return_value={"checklist_machine": machine_data, "checklist_issues": []})

    with patch("handlers.checklists.add_coffee_machine", new_callable=AsyncMock) as add_machine:
        await save_checklist(callback, state)

    add_machine.assert_called_once_with(machine_data)
    state.clear.assert_called_once()
    callback.message.answer.assert_called_once()
