import pandas as pd
from pathlib import Path

DATA_FILE = Path("C:/Users/jvict/Desktop/Pamela s2/Teste Prático - Dados para Tarefa 2 .xlsx")

xls = pd.ExcelFile(DATA_FILE)
sheet_map = {name.lower(): name for name in xls.sheet_names}
str_name = sheet_map.get("strings", "Strings")
df_str = pd.read_excel(xls, sheet_name=str_name, nrows=5)

for col in df_str.columns:
    if 'MPPT' in col or 'mppt' in col.lower():
        print("MPPT Column Found:", col)
