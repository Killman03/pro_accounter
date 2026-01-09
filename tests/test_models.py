import pytest
from datetime import date
from models import CoffeeMachine, Payment


class TestCoffeeMachineModel:
    """Тесты для Pydantic модели CoffeeMachine"""
    
    def test_create_coffee_machine_minimal(self):
        """Тест создания кофемашины с минимальными данными"""
        machine = CoffeeMachine(
            model="Saeco Lirika",
            barcode="123456789",
            rent_price=50000.0,
            tenant="Иван Иванов",
            phone="996555123456",
            deposit=100000.0,
            start_date=date(2024, 1, 1)
        )
        
        assert machine.model == "Saeco Lirika"
        assert machine.barcode == "123456789"
        assert machine.rent_price == 50000.0
        assert machine.tenant == "Иван Иванов"
        assert machine.phone == "996555123456"
        assert machine.deposit == 100000.0
        assert machine.start_date == date(2024, 1, 1)
        assert machine.in_1C is False
        assert machine.status == "active"
        assert machine.buyout is False
        assert machine.buyout_date is None
        assert machine.payments == []
        assert machine.deal_type == "Аренда"
        assert machine.comment is None
        assert machine.full_price is None
    
    def test_create_coffee_machine_full(self):
        """Тест создания кофемашины со всеми полями"""
        machine = CoffeeMachine(
            id=1,
            model="Saeco Lirika",
            barcode="123456789",
            rent_price=50000.0,
            tenant="Иван Иванов",
            phone="996555123456",
            deposit=100000.0,
            start_date=date(2024, 1, 1),
            in_1C=True,
            status="active",
            buyout=False,
            buyout_date=None,
            payments=[date(2024, 1, 15)],
            deal_type="Рассрочка",
            comment="Тестовый комментарий",
            full_price=300000.0
        )
        
        assert machine.id == 1
        assert machine.in_1C is True
        assert machine.status == "active"
        assert machine.payments == [date(2024, 1, 15)]
        assert machine.deal_type == "Рассрочка"
        assert machine.comment == "Тестовый комментарий"
        assert machine.full_price == 300000.0
    
    def test_coffee_machine_default_values(self):
        """Тест значений по умолчанию"""
        machine = CoffeeMachine(
            model="Saeco Lirika",
            barcode="123456789",
            rent_price=50000.0,
            tenant="Иван Иванов",
            phone="996555123456",
            deposit=100000.0,
            start_date=date(2024, 1, 1)
        )
        
        assert machine.in_1C is False
        assert machine.status == "active"
        assert machine.buyout is False
        assert machine.deal_type == "Аренда"
    
    def test_coffee_machine_with_buyout(self):
        """Тест кофемашины с выкупом"""
        machine = CoffeeMachine(
            model="Saeco Lirika",
            barcode="123456789",
            rent_price=50000.0,
            tenant="Иван Иванов",
            phone="996555123456",
            deposit=100000.0,
            start_date=date(2024, 1, 1),
            buyout=True,
            buyout_date=date(2024, 6, 1),
            status="buyout"
        )
        
        assert machine.buyout is True
        assert machine.buyout_date == date(2024, 6, 1)
        assert machine.status == "buyout"


class TestPaymentModel:
    """Тесты для Pydantic модели Payment"""
    
    def test_create_payment_minimal(self):
        """Тест создания платежа с минимальными данными"""
        payment = Payment(
            machine_id=1,
            tenant="Иван Иванов",
            amount=50000.0,
            payment_date=date(2024, 1, 15)
        )
        
        assert payment.machine_id == 1
        assert payment.tenant == "Иван Иванов"
        assert payment.amount == 50000.0
        assert payment.payment_date == date(2024, 1, 15)
        assert payment.is_deposit is False
        assert payment.is_buyout is False
    
    def test_create_payment_full(self):
        """Тест создания платежа со всеми полями"""
        payment = Payment(
            id=1,
            machine_id=1,
            tenant="Иван Иванов",
            amount=50000.0,
            payment_date=date(2024, 1, 15),
            is_deposit=True,
            is_buyout=False
        )
        
        assert payment.id == 1
        assert payment.is_deposit is True
        assert payment.is_buyout is False
    
    def test_create_payment_buyout(self):
        """Тест создания платежа выкупа"""
        payment = Payment(
            machine_id=1,
            tenant="Иван Иванов",
            amount=200000.0,
            payment_date=date(2024, 6, 1),
            is_deposit=False,
            is_buyout=True
        )
        
        assert payment.is_buyout is True
        assert payment.is_deposit is False
        assert payment.amount == 200000.0
    
    def test_payment_default_values(self):
        """Тест значений по умолчанию для платежа"""
        payment = Payment(
            machine_id=1,
            tenant="Иван Иванов",
            amount=50000.0,
            payment_date=date(2024, 1, 15)
        )
        
        assert payment.is_deposit is False
        assert payment.is_buyout is False



