import pandas as pd
from pathlib import Path

DATA_FILE = Path("C:/Users/jvict/Desktop/Pamela s2/Teste Prático - Dados para Tarefa 2 .xlsx")

xls = pd.ExcelFile(DATA_FILE)

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)
    # Pandas automatically appends .1, .2, etc to duplicates
    dupes = [col for col in df.columns if col.endswith('.1') or col.endswith('.2')]
    if dupes:
        print(f"--- Sheet: {sheet} ---")
        for d in dupes:
            print(f"Found duplicate column: {d}")
