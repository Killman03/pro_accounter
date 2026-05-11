from datetime import date
from types import SimpleNamespace

from utils.checklist_parser import parse_checklist_text


def test_parse_checklist_with_message_date_and_local_phone():
    models = [SimpleNamespace(name="SES 880")]
    text = """[25.04.2026 12:22] Ивасик: Чек лист

ФИО Камчибекова А
Модель ses 880
Штрих: SAGE254SJ32CE
Цена 55000
Аренда  5000
Депозит 5000
Телефон: 0502280928
Дата первой оплаты сегодня
Отметка - ж+в
Коммент: деньги у Жени"""

    parsed = parse_checklist_text(text, models, reference_date=date(2026, 5, 11))

    assert parsed.issues == []
    assert parsed.values["tenant"] == "Камчибекова А"
    assert parsed.values["model"] == "SES 880"
    assert parsed.values["barcode"] == "SAGE254SJ32CE"
    assert parsed.values["full_price"] == 55000
    assert parsed.values["rent_price"] == 5000
    assert parsed.values["deposit"] == 5000
    assert parsed.values["phone"] == "996502280928"
    assert parsed.values["start_date"] == date(2026, 4, 25)
    assert parsed.values["comment"] == "Отметка: ж+в; деньги у Жени"


def test_parse_checklist_date_line_nbsp_phone_and_model_by_number():
    models = [SimpleNamespace(name="SES 990")]
    text = """[02.05.2026 09:19] Массаж: Чек лист
ФИО Усупбаева Нуржан
Модель 990 черн.
Штрих A1SGFESA212401158
Цена 110000
Аренда 10000
Депозит 7000
Телефон  +996 705300384
Дата: 02.05.26
Отметка: Сергей
Комментарий:деньги у Жени"""

    parsed = parse_checklist_text(text, models)

    assert parsed.issues == []
    assert parsed.values["model"] == "SES 990"
    assert parsed.values["phone"] == "996705300384"
    assert parsed.values["start_date"] == date(2026, 5, 2)
    assert parsed.values["comment"] == "Отметка: Сергей; деньги у Жени"


def test_parse_checklist_reports_missing_barcode_and_installation_date():
    models = [SimpleNamespace(name="SES 990")]
    text = """[05.05.2026 14:41] Ивасик: Чек лист

ФИО Алимбаева Зарема Хамытжанова
Модель ses 990
Штрих
Цена 110000
Аренда 10000
Депозит 15000
Телефон: 0558988088
Дата первой оплаты - в день установки
Отметка - только Ваня
Коммент: - Оставили предоплату, ждут установку 7мая"""

    parsed = parse_checklist_text(text, models)

    assert "Штрих не указан" in parsed.issues
    assert "Дата первой оплаты: укажите дату вместо 'в день установки'" in parsed.issues
    assert parsed.values["phone"] == "996558988088"
