import plotly.graph_objects as go
from io import BytesIO

# 1. Динамика платежей
async def plot_payments_dynamic(data):
    fig = go.Figure()
    # data: [{'month': '2024-01', 'sum': 10000}, ...]
    fig.add_trace(go.Scatter(x=[d['month'] for d in data], y=[d['sum'] for d in data], mode='lines+markers'))
    fig.update_layout(title='Динамика платежей по месяцам')
    return await fig_to_bytesio(fig)

# 2. Топ моделей
async def plot_top_models(data):
    fig = go.Figure()
    # data: [{'model': 'Saeco', 'count': 5}, ...]
    fig.add_trace(go.Pie(labels=[d['model'] for d in data], values=[d['count'] for d in data]))
    fig.update_layout(title='Топ моделей')
    return await fig_to_bytesio(fig)

# 3. Ожидаемые платежи
async def plot_expected_payments(data):
    fig = go.Figure()
    # data: [{'tenant': 'Иванов', 'sum': 5000}, ...]
    fig.add_trace(go.Bar(x=[d['tenant'] for d in data], y=[d['sum'] for d in data]))
    fig.update_layout(title='Ожидаемые платежи')
    return await fig_to_bytesio(fig)

# 4. Просрочки
async def plot_overdue(data):
    fig = go.Figure()
    # data: [{'tenant': 'Иванов', 'days': 5}, ...]
    fig.add_trace(go.Bar(x=[d['tenant'] for d in data], y=[d['days'] for d in data], marker_color='red'))
    fig.update_layout(title='Просрочки')
    return await fig_to_bytesio(fig)

async def fig_to_bytesio(fig):
    img_bytes = fig.to_image(format='png')
    return BytesIO(img_bytes) 