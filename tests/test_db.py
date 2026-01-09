import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
from sqlalchemy import select, update, delete
from db import (
    get_all_machine_models,
    add_machine_model,
    delete_machine_model,
    add_coffee_machine,
    get_all_machines,
    add_payment,
    get_payments_by_machine,
    update_machine_status,
    get_machine_model_by_name,
    update_machine_full_price,
    update_machine_deal_type,
    update_machine_1c,
    update_machine_rent_price,
    get_last_payment_date
)
from models import CoffeeMachineORM, PaymentORM, MachineModelORM


class TestMachineModels:
    """Тесты для работы с моделями кофемашин"""
    
    @pytest.mark.asyncio
    async def test_get_all_machine_models(self, mock_machine_model):
        """Тест получения всех моделей кофемашин"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_machine_model]
            mock_session.execute.return_value = mock_result
            
            result = await get_all_machine_models()
            
            assert len(result) == 1
            assert result[0].name == "Saeco Lirika"
            mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_machine_model(self, mock_machine_model):
        """Тест добавления модели кофемашины"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_session.refresh = AsyncMock()
            mock_session.commit = AsyncMock()
            
            with patch('db.MachineModelORM') as mock_model_class:
                mock_model_instance = MagicMock()
                mock_model_instance.id = 1
                mock_model_class.return_value = mock_model_instance
                
                result = await add_machine_model("Test Model", 50000.0, 300000.0)
                
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_machine_model(self):
        """Тест удаления модели кофемашины"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            await delete_machine_model(1)
            
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_machine_model_by_name(self, mock_machine_model):
        """Тест получения модели по имени"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_machine_model
            mock_session.execute.return_value = mock_result
            
            result = await get_machine_model_by_name("Saeco Lirika")
            
            assert result is not None
            assert result.name == "Saeco Lirika"
            mock_session.execute.assert_called_once()


class TestCoffeeMachines:
    """Тесты для работы с кофемашинами"""
    
    @pytest.mark.asyncio
    async def test_add_coffee_machine(self, sample_machine_data):
        """Тест добавления кофемашины"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_machine = MagicMock()
            mock_machine.id = 1
            mock_session.refresh = AsyncMock()
            mock_session.commit = AsyncMock()
            
            with patch('db.CoffeeMachineORM') as mock_machine_class:
                mock_machine_class.return_value = mock_machine
                
                result = await add_coffee_machine(sample_machine_data)
                
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_machines(self, mock_coffee_machine):
        """Тест получения всех кофемашин"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_coffee_machine]
            mock_session.execute.return_value = mock_result
            
            result = await get_all_machines()
            
            assert len(result) == 1
            assert result[0].model == "Saeco Lirika"
            mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_machine_status(self):
        """Тест обновления статуса кофемашины"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            await update_machine_status(1, "buyout", buyout=True, buyout_date=date(2024, 6, 1))
            
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_machine_status_without_buyout_date(self):
        """Тест обновления статуса без даты выкупа"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            await update_machine_status(1, "returned", buyout=False)
            
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_machine_full_price(self):
        """Тест обновления полной стоимости кофемашины"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            await update_machine_full_price(1, 350000.0)
            
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_machine_deal_type(self):
        """Тест обновления типа сделки"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            await update_machine_deal_type(1, "Рассрочка")
            
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_machine_1c(self):
        """Тест обновления статуса 1С"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            await update_machine_1c(1, True)
            
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_machine_rent_price(self):
        """Тест обновления цены аренды"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            await update_machine_rent_price(1, 60000.0)
            
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()


class TestPayments:
    """Тесты для работы с платежами"""
    
    @pytest.mark.asyncio
    async def test_add_payment(self, sample_payment_data):
        """Тест добавления платежа"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_payment = MagicMock()
            mock_payment.id = 1
            mock_session.refresh = AsyncMock()
            mock_session.commit = AsyncMock()
            
            with patch('db.PaymentORM') as mock_payment_class:
                mock_payment_class.return_value = mock_payment
                
                result = await add_payment(sample_payment_data)
                
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_payments_by_machine(self, mock_payment):
        """Тест получения платежей по кофемашине"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_payment]
            mock_session.execute.return_value = mock_result
            
            result = await get_payments_by_machine(1)
            
            assert len(result) == 1
            assert result[0].machine_id == 1
            mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_last_payment_date(self):
        """Тест получения даты последнего платежа"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            test_date = date(2024, 1, 15)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = test_date
            mock_session.execute.return_value = mock_result
            
            result = await get_last_payment_date(1)
            
            assert result == test_date
            mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_last_payment_date_none(self):
        """Тест получения даты последнего платежа когда платежей нет"""
        with patch('db.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            result = await get_last_payment_date(1)
            
            assert result is None
            mock_session.execute.assert_called_once()



