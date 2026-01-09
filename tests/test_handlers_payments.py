import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, timedelta
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.payments import (
    start_payments,
    select_machine_for_payment,
    select_payment_type,
    input_payment_amount,
    input_payment_date,
    AddPayment
)


class TestStartPayments:
    """Тесты для начала работы с платежами"""
    
    @pytest.mark.asyncio
    async def test_start_payments_with_active_machines(self, mock_coffee_machine, mock_machine_model):
        """Тест начала платежей когда есть активные машины"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.payments.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                with patch('handlers.payments.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                    await start_payments(mock_msg, mock_state)
                    
                    mock_msg.answer.assert_called_once()
                    mock_state.set_state.assert_called_once_with(AddPayment.select_machine)
    
    @pytest.mark.asyncio
    async def test_start_payments_no_active_machines(self):
        """Тест начала платежей когда нет активных машин"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_machine = MagicMock()
        mock_machine.status = "buyout"
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_machine]):
            await start_payments(mock_msg, mock_state)
            
            mock_msg.answer.assert_called_once()
            assert "нет" in mock_msg.answer.call_args[0][0].lower() or "активных" in mock_msg.answer.call_args[0][0].lower()


class TestSelectMachineForPayment:
    """Тесты для выбора машины для платежа"""
    
    @pytest.mark.asyncio
    async def test_select_machine_for_payment(self):
        """Тест выбора машины для платежа"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "machine_1"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await select_machine_for_payment(mock_callback, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddPayment.payment_type)
        mock_callback.answer.assert_called_once()


class TestSelectPaymentType:
    """Тесты для выбора типа платежа"""
    
    @pytest.mark.asyncio
    async def test_select_payment_type_rent(self, mock_coffee_machine, mock_machine_model):
        """Тест выбора типа платежа - аренда"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "type_rent"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await select_payment_type(mock_callback, mock_state)
            
            mock_state.update_data.assert_called_once()
            mock_callback.message.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(AddPayment.amount)
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_select_payment_type_deposit(self, mock_coffee_machine, mock_machine_model):
        """Тест выбора типа платежа - депозит"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "type_deposit"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await select_payment_type(mock_callback, mock_state)
            
            mock_state.update_data.assert_called_once()
            mock_callback.message.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(AddPayment.amount)
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_select_payment_type_buyout(self, mock_coffee_machine, mock_machine_model):
        """Тест выбора типа платежа - выкуп"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "type_buyout"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.payments.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                with patch('handlers.payments.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                    await select_payment_type(mock_callback, mock_state)
                    
                    mock_state.update_data.assert_called_once()
                    mock_callback.message.answer.assert_called_once()
                    mock_state.set_state.assert_called_once_with(AddPayment.amount)
                    mock_callback.answer.assert_called_once()


class TestInputPaymentAmount:
    """Тесты для ввода суммы платежа"""
    
    @pytest.mark.asyncio
    async def test_input_payment_amount_default_rent(self, mock_coffee_machine):
        """Тест ввода суммы платежа - значение по умолчанию для аренды"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "."
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1, "payment_type": "rent"})
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await input_payment_amount(mock_msg, mock_state)
            
            mock_state.update_data.assert_called_once()
            mock_msg.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(AddPayment.payment_date)
    
    @pytest.mark.asyncio
    async def test_input_payment_amount_custom(self, mock_coffee_machine):
        """Тест ввода суммы платежа - пользовательское значение"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "60000"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1, "payment_type": "rent"})
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await input_payment_amount(mock_msg, mock_state)
            
            mock_state.update_data.assert_called_once()
            mock_msg.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(AddPayment.payment_date)
    
    @pytest.mark.asyncio
    async def test_input_payment_amount_invalid(self):
        """Тест ввода суммы платежа - невалидное значение"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1, "payment_type": "rent"})
        
        await input_payment_amount(mock_msg, mock_state)
        
        mock_state.update_data.assert_not_called()
        mock_msg.answer.assert_called_once()
        assert "корректную" in mock_msg.answer.call_args[0][0].lower() or "число" in mock_msg.answer.call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_input_payment_amount_buyout_requires_value(self, mock_coffee_machine):
        """Тест ввода суммы платежа - выкуп требует конкретное значение"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "."
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1, "payment_type": "buyout"})
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await input_payment_amount(mock_msg, mock_state)
            
            mock_state.update_data.assert_not_called()
            mock_msg.answer.assert_called_once()
            assert "конкретную" in mock_msg.answer.call_args[0][0].lower() or "выкуп" in mock_msg.answer.call_args[0][0].lower()


class TestInputPaymentDate:
    """Тесты для ввода даты платежа"""
    
    @pytest.mark.asyncio
    async def test_input_payment_date_today(self, mock_coffee_machine):
        """Тест ввода даты платежа - сегодня"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "."
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={
            "machine_id": 1,
            "payment_type": "rent",
            "amount": 50000.0
        })
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.payments.add_payment', new_callable=AsyncMock):
                with patch('handlers.payments.AsyncSessionLocal') as mock_session_local:
                    mock_session = AsyncMock()
                    mock_session_local.return_value.__aenter__.return_value = mock_session
                    mock_session.execute = AsyncMock()
                    mock_session.commit = AsyncMock()
                    
                    await input_payment_date(mock_msg, mock_state)
                    
                    mock_msg.answer.assert_called_once()
                    mock_state.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_input_payment_date_custom(self, mock_coffee_machine):
        """Тест ввода даты платежа - пользовательская дата"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "15-01-2024"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={
            "machine_id": 1,
            "payment_type": "rent",
            "amount": 50000.0
        })
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.payments.add_payment', new_callable=AsyncMock):
                with patch('handlers.payments.AsyncSessionLocal') as mock_session_local:
                    mock_session = AsyncMock()
                    mock_session_local.return_value.__aenter__.return_value = mock_session
                    mock_session.execute = AsyncMock()
                    mock_session.commit = AsyncMock()
                    
                    await input_payment_date(mock_msg, mock_state)
                    
                    mock_msg.answer.assert_called_once()
                    mock_state.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_input_payment_date_invalid(self):
        """Тест ввода даты платежа - невалидная дата"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid-date"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_payment_date(mock_msg, mock_state)
        
        mock_state.update_data.assert_not_called()
        mock_msg.answer.assert_called_once()
        assert "формате" in mock_msg.answer.call_args[0][0].lower() or "дату" in mock_msg.answer.call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_input_payment_date_buyout_updates_status(self, mock_coffee_machine):
        """Тест ввода даты платежа - выкуп обновляет статус"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "01-06-2024"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={
            "machine_id": 1,
            "payment_type": "buyout",
            "amount": 200000.0
        })
        
        with patch('handlers.payments.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.payments.add_payment', new_callable=AsyncMock):
                with patch('handlers.payments.AsyncSessionLocal') as mock_session_local:
                    mock_session = AsyncMock()
                    mock_session_local.return_value.__aenter__.return_value = mock_session
                    mock_session.execute = AsyncMock()
                    mock_session.commit = AsyncMock()
                    
                    await input_payment_date(mock_msg, mock_state)
                    
                    mock_session.execute.assert_called()
                    mock_session.commit.assert_called()
                    mock_msg.answer.assert_called_once()
                    mock_state.clear.assert_called_once()

