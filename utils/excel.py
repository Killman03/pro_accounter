import pandas as pd
from io import BytesIO

def generate_excel_report(active_machines_data: list[dict], payments_data: list[dict], closed_machines_data: list[dict] = None) -> BytesIO:
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Первый лист - активные кофемашины
        df_active = pd.DataFrame(active_machines_data)
        df_active.to_excel(writer, sheet_name='Активные сделки', index=False)
        
        # Второй лист - платежи
        df_payments = pd.DataFrame(payments_data)
        df_payments.to_excel(writer, sheet_name='Платежи', index=False)
        
        # Третий лист - закрытые сделки (если есть данные)
        if closed_machines_data:
            df_closed = pd.DataFrame(closed_machines_data)
            df_closed.to_excel(writer, sheet_name='Закрытые сделки', index=False)
    
    output.seek(0)
    return output 