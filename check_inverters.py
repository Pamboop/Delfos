import pandas as pd
from pathlib import Path

DATA_FILE = Path("C:/Users/jvict/Desktop/Pamela s2/Teste Prático - Dados para Tarefa 2 .xlsx")

xls = pd.ExcelFile(DATA_FILE)
sheet_map = {name.lower(): name for name in xls.sheet_names}
inv_name = sheet_map.get("inverters", "Inverters")
df_inv = pd.read_excel(xls, sheet_name=inv_name, nrows=5)

print("Inverter columns:")
for col in df_inv.columns:
    print(col)
