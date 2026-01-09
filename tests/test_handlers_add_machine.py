import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.add_machine import (
    start_add_machine,
    select_model,
    input_barcode,
    input_rent_price,
    input_tenant,
    input_phone,
    input_deposit,
    input_in1c,
    input_deal_type,
    input_comment,
    AddMachine
)


class TestStartAddMachine:
    """Тесты для начала добавления кофемашины"""
    
    @pytest.mark.asyncio
    async def test_start_add_machine_with_models(self, mock_machine_model):
        """Тест начала добавления когда есть модели"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.add_machine.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
            await start_add_machine(mock_msg, mock_state)
            
            mock_msg.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(AddMachine.model)
    
    @pytest.mark.asyncio
    async def test_start_add_machine_no_models(self):
        """Тест начала добавления когда нет моделей"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.add_machine.get_all_machine_models', new_callable=AsyncMock, return_value=[]):
            await start_add_machine(mock_msg, mock_state)
            
            mock_msg.answer.assert_called_once()
            assert "нет" in mock_msg.answer.call_args[0][0].lower() or "моделей" in mock_msg.answer.call_args[0][0].lower()


class TestSelectModel:
    """Тесты для выбора модели"""
    
    @pytest.mark.asyncio
    async def test_select_model_valid(self, mock_machine_model):
        """Тест выбора валидной модели"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "model_1"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.add_machine.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
            await select_model(mock_callback, mock_state)
            
            mock_state.update_data.assert_called()
            mock_callback.message.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(AddMachine.barcode)
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_select_model_not_found(self):
        """Тест выбора несуществующей модели"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "model_999"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.add_machine.get_all_machine_models', new_callable=AsyncMock, return_value=[]):
            await select_model(mock_callback, mock_state)
            
            mock_callback.message.answer.assert_called_once()
            assert "не найдена" in mock_callback.message.answer.call_args[0][0].lower()
            mock_callback.answer.assert_called_once()


class TestInputBarcode:
    """Тесты для ввода штрих-кода"""
    
    @pytest.mark.asyncio
    async def test_input_barcode(self):
        """Тест ввода штрих-кода"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "123456789"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"rent_price": 50000.0})
        
        await input_barcode(mock_msg, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_msg.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.rent_price)


class TestInputRentPrice:
    """Тесты для ввода цены аренды"""
    
    @pytest.mark.asyncio
    async def test_input_rent_price_default(self):
        """Тест ввода цены аренды - значение по умолчанию"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "."
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_rent_price(mock_msg, mock_state)
        
        mock_state.update_data.assert_not_called()
        mock_msg.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.tenant)
    
    @pytest.mark.asyncio
    async def test_input_rent_price_custom(self):
        """Тест ввода цены аренды - пользовательское значение"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "60000"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_rent_price(mock_msg, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_msg.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.tenant)
    
    @pytest.mark.asyncio
    async def test_input_rent_price_invalid(self):
        """Тест ввода цены аренды - невалидное значение"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_rent_price(mock_msg, mock_state)
        
        mock_state.update_data.assert_not_called()
        mock_msg.answer.assert_called_once()
        assert "число" in mock_msg.answer.call_args[0][0].lower()


class TestInputTenant:
    """Тесты для ввода арендатора"""
    
    @pytest.mark.asyncio
    async def test_input_tenant(self):
        """Тест ввода арендатора"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "Иван Иванов"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_tenant(mock_msg, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_msg.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.phone)


class TestInputPhone:
    """Тесты для ввода телефона"""
    
    @pytest.mark.asyncio
    async def test_input_phone_valid(self):
        """Тест ввода валидного телефона"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "996555123456"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.add_machine.validate_kg_phone', return_value=True):
            await input_phone(mock_msg, mock_state)
            
            mock_state.update_data.assert_called_once()
            mock_msg.answer.assert_called_once()
            mock_state.set_state.assert_called_once_with(AddMachine.deposit)
    
    @pytest.mark.asyncio
    async def test_input_phone_invalid(self):
        """Тест ввода невалидного телефона"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('handlers.add_machine.validate_kg_phone', return_value=False):
            await input_phone(mock_msg, mock_state)
            
            mock_state.update_data.assert_not_called()
            mock_msg.answer.assert_called_once()
            assert "формате" in mock_msg.answer.call_args[0][0].lower() or "996" in mock_msg.answer.call_args[0][0]


class TestInputDeposit:
    """Тесты для ввода депозита"""
    
    @pytest.mark.asyncio
    async def test_input_deposit_valid(self):
        """Тест ввода валидного депозита"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "100000"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_deposit(mock_msg, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_msg.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.in_1C)
    
    @pytest.mark.asyncio
    async def test_input_deposit_invalid(self):
        """Тест ввода невалидного депозита"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "invalid"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_deposit(mock_msg, mock_state)
        
        mock_state.update_data.assert_not_called()
        mock_msg.answer.assert_called_once()
        assert "число" in mock_msg.answer.call_args[0][0].lower()


class TestInputIn1C:
    """Тесты для ввода статуса 1С"""
    
    @pytest.mark.asyncio
    async def test_input_in1c_true(self):
        """Тест выбора статуса 1С - В 1С"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "in1c_true"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_in1c(mock_callback, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.deal_type)
        mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_input_in1c_false(self):
        """Тест выбора статуса 1С - Без 1С"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "in1c_false"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_in1c(mock_callback, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.deal_type)
        mock_callback.answer.assert_called_once()


class TestInputDealType:
    """Тесты для ввода типа сделки"""
    
    @pytest.mark.asyncio
    async def test_input_deal_type_rent(self):
        """Тест выбора типа сделки - Аренда"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "dealtype_rent"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_deal_type(mock_callback, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.comment)
        mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_input_deal_type_installment(self):
        """Тест выбора типа сделки - Рассрочка"""
        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.data = "dealtype_installment"
        mock_callback.message = AsyncMock(spec=Message)
        mock_callback.message.answer = AsyncMock()
        mock_callback.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        
        await input_deal_type(mock_callback, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(AddMachine.comment)
        mock_callback.answer.assert_called_once()


class TestInputComment:
    """Тесты для ввода комментария"""
    
    @pytest.mark.asyncio
    async def test_input_comment_with_text(self):
        """Тест ввода комментария с текстом"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "Тестовый комментарий"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={
            "model": "Saeco Lirika",
            "barcode": "123456789",
            "rent_price": 50000.0,
            "tenant": "Иван Иванов",
            "phone": "996555123456",
            "deposit": 100000.0,
            "in_1C": False,
            "deal_type": "Аренда",
            "comment": None
        })
        
        with patch('handlers.add_machine.add_coffee_machine', new_callable=AsyncMock):
            await input_comment(mock_msg, mock_state)
            
            mock_state.update_data.assert_called()
            mock_msg.answer.assert_called_once()
            mock_state.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_input_comment_with_dash(self):
        """Тест ввода комментария с дефисом (нет комментария)"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.text = "-"
        mock_msg.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={
            "model": "Saeco Lirika",
            "barcode": "123456789",
            "rent_price": 50000.0,
            "tenant": "Иван Иванов",
            "phone": "996555123456",
            "deposit": 100000.0,
            "in_1C": False,
            "deal_type": "Аренда",
            "comment": None
        })
        
        with patch('handlers.add_machine.add_coffee_machine', new_callable=AsyncMock):
            await input_comment(mock_msg, mock_state)
            
            mock_state.update_data.assert_called()
            mock_msg.answer.assert_called_once()
            mock_state.clear.assert_called_once()

