import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, timedelta
from aiogram.types import Message
from handlers.reports import send_excel_report, choose_plot, send_summary, send_profit_share


class TestSendExcelReport:
    """Тесты для отправки Excel отчета"""
    
    @pytest.mark.asyncio
    async def test_send_excel_report_with_active_machines(self, mock_coffee_machine, mock_machine_model):
        """Тест отправки Excel отчета с активными машинами"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer_document = AsyncMock()
        
        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.reports.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                with patch('handlers.reports.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                    with patch('handlers.reports.generate_excel_report') as mock_generate:
                        mock_file = MagicMock()
                        mock_file.read.return_value = b"test content"
                        mock_generate.return_value = mock_file
                        
                        await send_excel_report(mock_msg)
                        
                        mock_msg.answer_document.assert_called_once()
                        mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_excel_report_with_closed_machines(self, mock_coffee_machine, mock_machine_model):
        """Тест отправки Excel отчета с закрытыми машинами"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer_document = AsyncMock()
        mock_closed_machine = MagicMock()
        mock_closed_machine.status = "buyout"
        mock_closed_machine.model = "Jura E8"
        mock_closed_machine.barcode = "987654321"
        mock_closed_machine.rent_price = 70000.0
        mock_closed_machine.tenant = "Петр Петров"
        mock_closed_machine.phone = "996555654321"
        mock_closed_machine.deposit = 150000.0
        mock_closed_machine.start_date = date(2024, 1, 1)
        mock_closed_machine.in_1C = True
        mock_closed_machine.deal_type = "Рассрочка"
        mock_closed_machine.comment = None
        mock_closed_machine.full_price = 400000.0
        
        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_closed_machine]):
            with patch('handlers.reports.get_all_machine_models', new_callable=AsyncMock, return_value=[mock_machine_model]):
                with patch('handlers.reports.get_payments_by_machine', new_callable=AsyncMock, return_value=[]):
                    with patch('handlers.reports.generate_excel_report') as mock_generate:
                        mock_file = MagicMock()
                        mock_file.read.return_value = b"test content"
                        mock_generate.return_value = mock_file
                        
                        await send_excel_report(mock_msg)
                        
                        mock_msg.answer_document.assert_called_once()
                        mock_generate.assert_called_once()


class TestChoosePlot:
    """Тесты для выбора графика"""
    
    @pytest.mark.asyncio
    async def test_choose_plot_with_data(self, mock_coffee_machine):
        """Тест выбора графика с данными"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer_photo = AsyncMock()
        
        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.reports.plot_top_models', new_callable=AsyncMock) as mock_plot:
                mock_file = MagicMock()
                mock_file.read.return_value = b"test image"
                mock_plot.return_value = mock_file
                
                await choose_plot(mock_msg)
                
                mock_msg.answer_photo.assert_called_once()
                mock_plot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_choose_plot_no_data(self):
        """Тест выбора графика без данных"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        
        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[]):
            with patch('handlers.reports.plot_top_models', new_callable=AsyncMock, return_value=None):
                await choose_plot(mock_msg)
                
                mock_msg.answer.assert_called_once()
                assert "нет данных" in mock_msg.answer.call_args[0][0].lower()


class TestSendSummary:
    """Тесты для отправки сводки"""
    
    @pytest.mark.asyncio
    async def test_send_summary_with_active_machines(self, mock_coffee_machine):
        """Тест отправки сводки с активными машинами"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        
        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.reports.get_last_payment_date', new_callable=AsyncMock, return_value=None):
                await send_summary(mock_msg)
                
                mock_msg.answer.assert_called_once()
                call_text = mock_msg.answer.call_args[0][0]
                assert "кофемашин" in call_text.lower() or "аренде" in call_text.lower()
    
    @pytest.mark.asyncio
    async def test_send_summary_with_overdue(self, mock_coffee_machine):
        """Тест отправки сводки с просроченными платежами"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        # Устанавливаем дату последнего платежа так, чтобы был просрочен
        old_date = date.today() - timedelta(days=35)
        
        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.reports.get_last_payment_date', new_callable=AsyncMock, return_value=old_date):
                await send_summary(mock_msg)
                
                mock_msg.answer.assert_called_once()
                call_text = mock_msg.answer.call_args[0][0]
                assert "просрочено" in call_text.lower() or "кофемашин" in call_text.lower()
    
    @pytest.mark.asyncio
    async def test_send_summary_no_active_machines(self):
        """Тест отправки сводки без активных машин"""
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer = AsyncMock()
        mock_machine = MagicMock()
        mock_machine.status = "buyout"
        
        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_machine]):
            await send_summary(mock_msg)
            
            mock_msg.answer.assert_called_once()
            call_text = mock_msg.answer.call_args[0][0]
            assert "0" in call_text or "кофемашин" in call_text.lower()


class TestSendProfitShare:
    @pytest.mark.asyncio
    async def test_profit_share_uses_actual_rent_payment_amount(self, mock_coffee_machine):
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer_document = AsyncMock()

        payment = MagicMock()
        payment.payment_date = date(2026, 2, 10)
        payment.amount = 8000.0
        payment.is_deposit = False
        payment.is_buyout = False

        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.reports.get_payments_by_machine', new_callable=AsyncMock, return_value=[payment]):
                with patch('handlers.reports.generate_profit_share_report') as mock_generate:
                    mock_file = MagicMock()
                    mock_file.read.return_value = b"profit"
                    mock_generate.return_value = mock_file

                    await send_profit_share(mock_msg)

                    rows = mock_generate.call_args[0][0]
                    assert len(rows) == 1
                    assert rows[0]["2026-02"] == 8000.0
                    mock_msg.answer_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_profit_share_does_not_fill_months_without_payments(self):
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer_document = AsyncMock()

        machine_1 = MagicMock()
        machine_1.id = 1
        machine_1.start_date = date(2026, 1, 1)
        machine_1.tenant = "Tenant 1"
        machine_1.model = "M1"
        machine_1.rent_price = 9000.0
        machine_1.status = "active"

        machine_2 = MagicMock()
        machine_2.id = 2
        machine_2.start_date = date(2026, 1, 1)
        machine_2.tenant = "Tenant 2"
        machine_2.model = "M2"
        machine_2.rent_price = 9000.0
        machine_2.status = "active"

        p_jan = MagicMock()
        p_jan.payment_date = date(2026, 1, 15)
        p_jan.amount = 9000.0
        p_jan.is_deposit = False
        p_jan.is_buyout = False

        p_feb = MagicMock()
        p_feb.payment_date = date(2026, 2, 15)
        p_feb.amount = 12000.0
        p_feb.is_deposit = False
        p_feb.is_buyout = False

        async def get_payments_side_effect(machine_id: int):
            return [p_jan] if machine_id == 1 else [p_feb]

        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[machine_1, machine_2]):
            with patch('handlers.reports.get_payments_by_machine', new_callable=AsyncMock, side_effect=get_payments_side_effect):
                with patch('handlers.reports.generate_profit_share_report') as mock_generate:
                    mock_file = MagicMock()
                    mock_file.read.return_value = b"profit"
                    mock_generate.return_value = mock_file

                    await send_profit_share(mock_msg)

                    rows = mock_generate.call_args[0][0]
                    assert "2026-02" not in rows[0]
                    assert "2026-01" not in rows[1]

    @pytest.mark.asyncio
    async def test_profit_share_includes_deposit_payments(self, mock_coffee_machine):
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer_document = AsyncMock()

        deposit_payment = MagicMock()
        deposit_payment.payment_date = date(2026, 3, 5)
        deposit_payment.amount = 15000.0
        deposit_payment.is_deposit = True
        deposit_payment.is_buyout = False

        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.reports.get_payments_by_machine', new_callable=AsyncMock, return_value=[deposit_payment]):
                with patch('handlers.reports.generate_profit_share_report') as mock_generate:
                    mock_file = MagicMock()
                    mock_file.read.return_value = b"profit"
                    mock_generate.return_value = mock_file

                    await send_profit_share(mock_msg)

                    rows = mock_generate.call_args[0][0]
                    assert rows[0]["2026-03"] == 15000.0

    @pytest.mark.asyncio
    async def test_profit_share_includes_deal_type_in_separate_column(self, mock_coffee_machine):
        mock_msg = AsyncMock(spec=Message)
        mock_msg.answer_document = AsyncMock()
        mock_coffee_machine.tenant = "Иван Иванов"
        mock_coffee_machine.deal_type = "Рассрочка"

        payment = MagicMock()
        payment.payment_date = date(2026, 4, 1)
        payment.amount = 10000.0
        payment.is_deposit = False
        payment.is_buyout = False

        with patch('handlers.reports.get_all_machines', new_callable=AsyncMock, return_value=[mock_coffee_machine]):
            with patch('handlers.reports.get_payments_by_machine', new_callable=AsyncMock, return_value=[payment]):
                with patch('handlers.reports.generate_profit_share_report') as mock_generate:
                    mock_file = MagicMock()
                    mock_file.read.return_value = b"profit"
                    mock_generate.return_value = mock_file

                    await send_profit_share(mock_msg)

                    rows = mock_generate.call_args[0][0]
                    assert rows[0]["Арендатор"] == "Иван Иванов"
                    assert rows[0]["Тип сделки"] == "Рассрочка"
