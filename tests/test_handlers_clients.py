import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, timedelta
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.clients import (
    get_client_info,
    show_clients,
    select_client,
    edit_price_start,
    edit_price_save,
    edit_dealtype_start,
    edit_dealtype_save,
    edit_1c_start,
    edit_1c_save,
    edit_rent_start,
    edit_rent_save,
    EditFSM
)


class TestGetClientInfo:
    """Тесты для получения информации о клиенте"""
    
    @pytest.mark.asyncio
    async def test_get_client_info(self, mock_coffee_machine, mock_machine_model):
        """Тест получения информации о клиенте"""
        with patch('handlers.clients.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
            with patch('handlers.clients.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                with patch('handlers.clients.get_last_payment_date', new_callable=AsyncMock, return_value=None):
                    info = await get_client_info(mock_coffee_machine)
                    
                    assert "Иван Иванов" in info
                    assert "996555123456" in info
                    assert "Saeco Lirika" in info
                    assert "50000" in info or "50000.0" in info
    
    @pytest.mark.asyncio
    async def test_get_client_info_with_payments(self, mock_coffee_machine, mock_machine_model, mock_payment):
        """Тест получения информации о клиенте с платежами"""
        with patch('handlers.clients.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
            with patch('handlers.clients.get_payments_by_machine', new_callable=AsyncMock, return_value=[mock_payment]):
                with patch('handlers.clients.get_last_payment_date', new_callable=AsyncMock, return_value=date(2024, 1, 15)):
                    info = await get_client_info(mock_coffee_machine)
                    
                    assert "Иван Иванов" in info
                    assert "50000" in info or "50000.0" in info


class TestShowClients:
    """Тесты для показа клиентов"""
    
    @pytest.mark.asyncio
    async def test_show_clients_with_active(self, mock_coffee_machine):
        """Тест показа клиентов когда есть активные"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.clients.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                with patch('handlers.clients.get_last_payment_date', new_callable=AsyncMock, return_value=None):
                    await show_clients(mock_msg, mock_state)
                    
                    mock_msg.answer.assert_called_once()
                    mock_state.set_state.assert_called_once_with(EditFSM.select_machine)
    
    @pytest.mark.asyncio
    async def test_show_clients_empty(self):
        """Тест показа клиентов когда список пуст"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[]):
            await show_clients(mock_msg, mock_state)
            
            mock_msg.answer.assert_called_once()
            assert "нет" in mock_msg.answer.call_args[0][0].lower() or "пуст" in mock_msg.answer.call_args[0][0].lower()


class TestSelectClient:
    """Тесты для выбора клиента"""
    
    @pytest.mark.asyncio
    async def test_select_client(self, mock_coffee_machine, mock_machine_model):
        """Тест выбора клиента"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "client_1"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.clients.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                with patch('handlers.clients.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                    with patch('handlers.clients.get_last_payment_date', new_callable=AsyncMock, return_value=None):
                        await select_client(mock_callback, mock_state)
                        
                        mock_callback.message.answer.assert_called()
                        mock_state.update_data.assert_called_once()
                        mock_state.set_state.assert_called_once_with(EditFSM.action)
                        mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_select_client_not_found(self):
        """Тест выбора несуществующего клиента"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "client_999"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[]):
            await select_client(mock_callback, mock_state)
            
            mock_callback.message.answer.assert_called_once()
            assert "не найден" in mock_callback.message.answer.call_args[0][0].lower()
            mock_callback.answer.assert_called_once()


class TestEditPrice:
    """Тесты для редактирования цены"""
    
    @pytest.mark.asyncio
    async def test_edit_price_start(self, mock_coffee_machine):
        """Тест начала редактирования цены"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await edit_price_start(mock_callback, mock_state)
            
            mock_callback.message.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(EditFSM.new_price)
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_price_save_valid(self, mock_coffee_machine, mock_machine_model):
        """Тест сохранения валидной цены"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "350000"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.clients.update_machine_full_price', new_callable=AsyncMock):
            with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
                with patch('handlers.clients.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                    with patch('handlers.clients.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                        with patch('handlers.clients.get_last_payment_date', new_callable=AsyncMock, return_value=None):
                            with patch('handlers.clients.get_client_info', new_callable=AsyncMock, return_value="Test info"):
                                await edit_price_save(mock_msg, mock_state)
                                
                                mock_msg.answer.assert_called()
                                mock_state.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_price_save_invalid(self):
        """Тест сохранения невалидной цены"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await edit_price_save(mock_msg, mock_state)
        
        mock_msg.answer.assert_called_once()
        assert "число" in mock_msg.answer.call_args[0][0].lower()


class TestEditDealType:
    """Тесты для редактирования типа сделки"""
    
    @pytest.mark.asyncio
    async def test_edit_dealtype_start(self, mock_coffee_machine):
        """Тест начала редактирования типа сделки"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await edit_dealtype_start(mock_callback, mock_state)
            
            mock_callback.message.answer.assert_called()
            mock_state.set_state.assert_called_once_with(EditFSM.new_deal_type)
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_dealtype_save_rent(self, mock_coffee_machine, mock_machine_model):
        """Тест сохранения типа сделки - Аренда"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "dealtype_rent"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.clients.update_machine_deal_type', new_callable=AsyncMock):
            with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
                with patch('handlers.clients.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                    with patch('handlers.clients.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                        with patch('handlers.clients.get_last_payment_date', new_callable=AsyncMock, return_value=None):
                            with patch('handlers.clients.get_client_info', new_callable=AsyncMock, return_value="Test info"):
                                await edit_dealtype_save(mock_callback, mock_state)
                                
                                mock_callback.message.answer.assert_called()
                                mock_state.clear.assert_called_once()
                                mock_callback.answer.assert_called_once()


class TestEdit1C:
    """Тесты для редактирования статуса 1С"""
    
    @pytest.mark.asyncio
    async def test_edit_1c_start(self, mock_coffee_machine):
        """Тест начала редактирования статуса 1С"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await edit_1c_start(mock_callback, mock_state)
            
            mock_callback.message.answer.assert_called()
            mock_state.set_state.assert_called_once_with(EditFSM.new_1c)
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_1c_save_true(self, mock_coffee_machine, mock_machine_model):
        """Тест сохранения статуса 1С - В 1С"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "1c_true"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.clients.update_machine_1c', new_callable=AsyncMock):
            with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
                with patch('handlers.clients.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                    with patch('handlers.clients.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                        with patch('handlers.clients.get_last_payment_date', new_callable=AsyncMock, return_value=None):
                            with patch('handlers.clients.get_client_info', new_callable=AsyncMock, return_value="Test info"):
                                await edit_1c_save(mock_callback, mock_state)
                                
                                mock_callback.message.answer.assert_called()
                                mock_state.clear.assert_called_once()
                                mock_callback.answer.assert_called_once()


class TestEditRent:
    """Тесты для редактирования аренды"""
    
    @pytest.mark.asyncio
    async def test_edit_rent_start(self, mock_coffee_machine):
        """Тест начала редактирования аренды"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            await edit_rent_start(mock_callback, mock_state)
            
            mock_callback.message.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(EditFSM.new_rent)
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_rent_save_valid(self, mock_coffee_machine, mock_machine_model):
        """Тест сохранения валидной аренды"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "60000"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"machine_id": 1})
        
        with patch('handlers.clients.update_machine_rent_price', new_callable=AsyncMock):
            with patch('handlers.clients.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
                with patch('handlers.clients.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                    with patch('handlers.clients.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                        with patch('handlers.clients.get_last_payment_date', new_callable=AsyncMock, return_value=None):
                            with patch('handlers.clients.get_client_info', new_callable=AsyncMock, return_value="Test info"):
                                await edit_rent_save(mock_msg, mock_state)
                                
                                mock_msg.answer.assert_called()
                                mock_state.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_rent_save_invalid(self):
        """Тест сохранения невалидной аренды"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await edit_rent_save(mock_msg, mock_state)
        
        mock_msg.answer.assert_called_once()
        assert "число" in mock_msg.answer.call_args[0][0].lower()

