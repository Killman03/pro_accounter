import pytest
from io import BytesIO
from utils.excel import generate_excel_report
import pandas as pd
from datetime import date


class TestGenerateExcelReport:
    """Тесты для генерации Excel отчетов"""
    
    def test_generate_excel_with_active_machines(self):
        """Тест генерации Excel с активными кофемашинами"""
        active_data = [
            {
                "Дата начала": date(2024, 1, 1),
                "Арендатор": "Иван Иванов",
                "Модель": "Saeco Lirika",
                "Штрих-код": "123456789",
                "Оплата": 50000.0,
                "Залог": 100000.0,
                "Полная стоимость": 300000.0,
                "Телефон": "996555123456",
                "1С_статус": False,
                "Статус": "Открыта",
                "Тип сделки": "Аренда",
                "Комментарий": "",
                "Остаток к выплате": 150000.0,
            }
        ]
        payments_data = []
        closed_data = None
        
        result = generate_excel_report(active_data, payments_data, closed_data)
        
        assert isinstance(result, BytesIO)
        assert result.tell() == 0  # Файл должен быть в начале
        
        # Проверяем что файл можно прочитать
        result.seek(0)
        df = pd.read_excel(result, sheet_name='Активные сделки')
        assert len(df) == 1
        assert df.iloc[0]['Арендатор'] == "Иван Иванов"
    
    def test_generate_excel_with_payments(self):
        """Тест генерации Excel с платежами"""
        active_data = []
        payments_data = [
            {
                "Модель кофемашины": "Saeco Lirika",
                "Арендатор": "Иван Иванов",
                "Сумма": 50000.0,
                "Дата платежа": date(2024, 1, 15),
                "Тип": "Аренда",
                "Остаток к доплате": 200000.0,
            }
        ]
        closed_data = None
        
        result = generate_excel_report(active_data, payments_data, closed_data)
        
        assert isinstance(result, BytesIO)
        result.seek(0)
        df = pd.read_excel(result, sheet_name='Платежи')
        assert len(df) == 1
        assert df.iloc[0]['Сумма'] == 50000.0
    
    def test_generate_excel_with_closed_machines(self):
        """Тест генерации Excel с закрытыми сделками"""
        active_data = []
        payments_data = []
        closed_data = [
            {
                "Дата начала": date(2024, 1, 1),
                "Арендатор": "Петр Петров",
                "Модель": "Jura E8",
                "Штрих-код": "987654321",
                "Оплата": 70000.0,
                "Залог": 150000.0,
                "Полная стоимость": 400000.0,
                "Телефон": "996555654321",
                "1С_статус": True,
                "Статус": "Закрыта (выкуп)",
                "Тип сделки": "Рассрочка",
                "Комментарий": "Выкуплена",
                "Остаток к выплате": 0.0,
            }
        ]
        
        result = generate_excel_report(active_data, payments_data, closed_data)
        
        assert isinstance(result, BytesIO)
        result.seek(0)
        df = pd.read_excel(result, sheet_name='Закрытые сделки')
        assert len(df) == 1
        assert df.iloc[0]['Статус'] == "Закрыта (выкуп)"
    
    def test_generate_excel_all_sheets(self):
        """Тест генерации Excel со всеми листами"""
        active_data = [{"Дата начала": date(2024, 1, 1), "Арендатор": "Иван", "Модель": "Saeco", 
                       "Штрих-код": "123", "Оплата": 50000, "Залог": 100000, "Полная стоимость": 300000,
                       "Телефон": "996555123456", "1С_статус": False, "Статус": "Открыта",
                       "Тип сделки": "Аренда", "Комментарий": "", "Остаток к выплате": 150000}]
        payments_data = [{"Модель кофемашины": "Saeco", "Арендатор": "Иван", "Сумма": 50000,
                          "Дата платежа": date(2024, 1, 15), "Тип": "Аренда", "Остаток к доплате": 200000}]
        closed_data = [{"Дата начала": date(2024, 1, 1), "Арендатор": "Петр", "Модель": "Jura",
                       "Штрих-код": "456", "Оплата": 70000, "Залог": 150000, "Полная стоимость": 400000,
                       "Телефон": "996555654321", "1С_статус": True, "Статус": "Закрыта (выкуп)",
                       "Тип сделки": "Рассрочка", "Комментарий": "", "Остаток к выплате": 0}]
        
        result = generate_excel_report(active_data, payments_data, closed_data)
        
        result.seek(0)
        # Проверяем все листы
        excel_file = pd.ExcelFile(result)
        assert 'Активные сделки' in excel_file.sheet_names
        assert 'Платежи' in excel_file.sheet_names
        assert 'Закрытые сделки' in excel_file.sheet_names
    
    def test_generate_excel_empty_data(self):
        """Тест генерации Excel с пустыми данными"""
        active_data = []
        payments_data = []
        closed_data = None
        
        result = generate_excel_report(active_data, payments_data, closed_data)
        
        assert isinstance(result, BytesIO)
        result.seek(0)
        df_active = pd.read_excel(result, sheet_name='Активные сделки')
        assert len(df_active) == 0



