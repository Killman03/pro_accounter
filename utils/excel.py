import pandas as pd
from io import BytesIO

def generate_excel_report(machines_data: list[dict], payments_data: list[dict] = None) -> BytesIO:
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Первый лист - кофемашины
        df_machines = pd.DataFrame(machines_data)
        df_machines.to_excel(writer, sheet_name='Кофемашины', index=False)
        
        # Второй лист - платежи (если есть данные)
        if payments_data:
            df_payments = pd.DataFrame(payments_data)
            df_payments.to_excel(writer, sheet_name='Платежи', index=False)
    
    output.seek(0)
    return output 