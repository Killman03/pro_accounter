import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.models import show_models, add_model_start, add_model_name, add_model_rent, add_model_full_price, del_model, ModelFSM


class TestShowModels:
    """Тесты для показа моделей"""
    
    @pytest.mark.asyncio
    async def test_show_models_with_models(self, mock_machine_model):
        """Тест показа моделей когда они есть"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.models.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
            await show_models(mock_msg, mock_state)
            
            mock_msg.answer.assert_called_once()
            call_args = mock_msg.answer.call_args
            assert "Saeco Lirika" in call_args[0][0] or "аренда: 50000" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_show_models_empty(self):
        """Тест показа моделей когда список пуст"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.models.get_all_machine_models', new_callable=AsyncMock, return_value=[]):
            await show_models(mock_msg, mock_state)
            
            mock_msg.answer.assert_called_once()
            call_args = mock_msg.answer.call_args
            assert "пуст" in call_args[0][0] or "Добавьте" in call_args[0][0]


class TestAddModel:
    """Тесты для добавления модели"""
    
    @pytest.mark.asyncio
    async def test_add_model_start(self):
        """Тест начала добавления модели"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await add_model_start(mock_callback, mock_state)
        
        mock_callback.message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(ModelFSM.add_name)
        mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_model_name(self):
        """Тест ввода названия модели"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "Test Model"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await add_model_name(mock_msg, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_msg.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(ModelFSM.add_rent)
    
    @pytest.mark.asyncio
    async def test_add_model_rent_valid(self):
        """Тест ввода валидной цены аренды"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "50000"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await add_model_rent(mock_msg, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_msg.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(ModelFSM.add_full_price)
    
    @pytest.mark.asyncio
    async def test_add_model_rent_invalid(self):
        """Тест ввода невалидной цены аренды"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await add_model_rent(mock_msg, mock_state)
        
        mock_state.update_data.assert_not_called()
        mock_msg.answer.assert_called_once()
        assert "число" in mock_msg.answer.call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_add_model_full_price_valid(self, mock_machine_model):
        """Тест ввода валидной полной стоимости"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "300000"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"name": "Test Model", "default_rent": 50000.0})
        
        with patch('handlers.models.add_machine_model', new_callable=AsyncMock, return_value=mock_machine_model):
            with patch('handlers.models.show_models', new_callable=AsyncMock) as mock_show:
                await add_model_full_price(mock_msg, mock_state)
                
                mock_state.update_data.assert_called_once()
                mock_msg.answer.assert_called_once()
                mock_state.clear.assert_called_once()
                mock_show.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_model_full_price_invalid(self):
        """Тест ввода невалидной полной стоимости"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await add_model_full_price(mock_msg, mock_state)
        
        mock_state.update_data.assert_not_called()
        mock_msg.answer.assert_called_once()
        assert "число" in mock_msg.answer.call_args[0][0].lower()


class TestDeleteModel:
    """Тесты для удаления модели"""
    
    @pytest.mark.asyncio
    async def test_del_model(self):
        """Тест удаления модели"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "del_model_1"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.models.delete_machine_model', new_callable=AsyncMock):
            with patch('handlers.models.show_models', new_callable=AsyncMock) as mock_show:
                await del_model(mock_callback, mock_state)
                
                mock_callback.message.answer.assert_called_once()
                mock_show.assert_called_once()
                mock_callback.answer.assert_called_once()

