import pytest
from io import BytesIO
from utils.plots import plot_top_models, plot_payments_dynamic, plot_expected_payments, plot_overdue, fig_to_bytesio
import plotly.graph_objects as go


class TestPlotTopModels:
    """Тесты для графика топ моделей"""
    
    @pytest.mark.asyncio
    async def test_plot_top_models_with_data(self):
        """Тест построения графика топ моделей с данными"""
        data = [
            {"model": "Saeco Lirika", "count": 5},
            {"model": "Jura E8", "count": 3},
            {"model": "DeLonghi Magnifica", "count": 2}
        ]
        
        result = await plot_top_models(data)
        
        assert isinstance(result, BytesIO)
        assert result.tell() == 0
    
    @pytest.mark.asyncio
    async def test_plot_top_models_empty_data(self):
        """Тест построения графика с пустыми данными"""
        data = []
        
        result = await plot_top_models(data)
        
        assert isinstance(result, BytesIO)
    
    @pytest.mark.asyncio
    async def test_plot_top_models_single_item(self):
        """Тест построения графика с одним элементом"""
        data = [{"model": "Saeco Lirika", "count": 1}]
        
        result = await plot_top_models(data)
        
        assert isinstance(result, BytesIO)


class TestPlotPaymentsDynamic:
    """Тесты для графика динамики платежей"""
    
    @pytest.mark.asyncio
    async def test_plot_payments_dynamic_with_data(self):
        """Тест построения графика динамики платежей"""
        data = [
            {"month": "2024-01", "sum": 100000},
            {"month": "2024-02", "sum": 150000},
            {"month": "2024-03", "sum": 120000}
        ]
        
        result = await plot_payments_dynamic(data)
        
        assert isinstance(result, BytesIO)
        assert result.tell() == 0
    
    @pytest.mark.asyncio
    async def test_plot_payments_dynamic_empty_data(self):
        """Тест построения графика с пустыми данными"""
        data = []
        
        result = await plot_payments_dynamic(data)
        
        assert isinstance(result, BytesIO)


class TestPlotExpectedPayments:
    """Тесты для графика ожидаемых платежей"""
    
    @pytest.mark.asyncio
    async def test_plot_expected_payments_with_data(self):
        """Тест построения графика ожидаемых платежей"""
        data = [
            {"tenant": "Иван Иванов", "sum": 50000},
            {"tenant": "Петр Петров", "sum": 70000}
        ]
        
        result = await plot_expected_payments(data)
        
        assert isinstance(result, BytesIO)
        assert result.tell() == 0
    
    @pytest.mark.asyncio
    async def test_plot_expected_payments_empty_data(self):
        """Тест построения графика с пустыми данными"""
        data = []
        
        result = await plot_expected_payments(data)
        
        assert isinstance(result, BytesIO)


class TestPlotOverdue:
    """Тесты для графика просрочек"""
    
    @pytest.mark.asyncio
    async def test_plot_overdue_with_data(self):
        """Тест построения графика просрочек"""
        data = [
            {"tenant": "Иван Иванов", "days": 5},
            {"tenant": "Петр Петров", "days": 10}
        ]
        
        result = await plot_overdue(data)
        
        assert isinstance(result, BytesIO)
        assert result.tell() == 0
    
    @pytest.mark.asyncio
    async def test_plot_overdue_empty_data(self):
        """Тест построения графика с пустыми данными"""
        data = []
        
        result = await plot_overdue(data)
        
        assert isinstance(result, BytesIO)


class TestFigToBytesio:
    """Тесты для конвертации графика в BytesIO"""
    
    @pytest.mark.asyncio
    async def test_fig_to_bytesio(self):
        """Тест конвертации графика в BytesIO"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3]))
        
        result = await fig_to_bytesio(fig)
        
        assert isinstance(result, BytesIO)
        assert result.tell() == 0
        # Проверяем что файл содержит данные
        result.seek(0)
        content = result.read()
        assert len(content) > 0



