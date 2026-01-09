import pytest
pytest_plugins = ("pytest_asyncio",)
from unittest.mock import AsyncMock, MagicMock, Mock
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from models import CoffeeMachineORM, PaymentORM, MachineModelORM


@pytest.fixture
def mock_machine_model():
    """Фикстура для создания мока модели кофемашины"""
    model = MagicMock(spec=MachineModelORM)
    model.id = 1
    model.name = "Saeco Lirika"
    model.default_rent = 50000.0
    model.full_price = 300000.0
    return model


@pytest.fixture
def mock_coffee_machine():
    """Фикстура для создания мока кофемашины"""
    machine = MagicMock(spec=CoffeeMachineORM)
    machine.id = 1
    machine.model = "Saeco Lirika"
    machine.barcode = "123456789"
    machine.rent_price = 50000.0
    machine.tenant = "Иван Иванов"
    machine.phone = "996555123456"
    machine.deposit = 100000.0
    machine.start_date = date(2024, 1, 1)
    machine.in_1C = False
    machine.status = "active"
    machine.buyout = False
    machine.buyout_date = None
    machine.payments = []
    machine.deal_type = "Аренда"
    machine.comment = None
    machine.full_price = 300000.0
    machine.payments_rel = []
    return machine


@pytest.fixture
def mock_payment():
    """Фикстура для создания мока платежа"""
    payment = MagicMock(spec=PaymentORM)
    payment.id = 1
    payment.machine_id = 1
    payment.tenant = "Иван Иванов"
    payment.amount = 50000.0
    payment.payment_date = date(2024, 1, 15)
    payment.is_deposit = False
    payment.is_buyout = False
    return payment


@pytest.fixture
def mock_async_session():
    """Фикстура для создания мока асинхронной сессии"""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def sample_machine_data():
    """Фикстура для данных кофемашины"""
    return {
        "model": "Saeco Lirika",
        "barcode": "123456789",
        "rent_price": 50000.0,
        "tenant": "Иван Иванов",
        "phone": "996555123456",
        "deposit": 100000.0,
        "start_date": date(2024, 1, 1),
        "in_1C": False,
        "status": "active",
        "buyout": False,
        "buyout_date": None,
        "payments": [],
        "deal_type": "Аренда",
        "comment": None,
        "full_price": 300000.0
    }


@pytest.fixture
def sample_payment_data():
    """Фикстура для данных платежа"""
    return {
        "machine_id": 1,
        "tenant": "Иван Иванов",
        "amount": 50000.0,
        "payment_date": date(2024, 1, 15),
        "is_deposit": False,
        "is_buyout": False
    }

