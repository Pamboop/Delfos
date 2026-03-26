import pandas as pd
import json

file_path = "c:/Users/jvict/Desktop/Pamela s2/Teste Prático - Dados para Tarefa 2 .xlsx"

print("Trying to load Excel sheets...")
try:
    xl = pd.ExcelFile(file_path)
    sheet_names = xl.sheet_names
    print(f"Sheet names: {sheet_names}")
    
    for sheet in sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = xl.parse(sheet, nrows=5)
        print("Columns:")
        print(df.columns.tolist())
        print("\nTypes:")
        print(df.dtypes.apply(lambda x: x.name).to_dict())
        print("\nHead:")
        print(df.head(2).to_dict(orient="records"))
        
except Exception as e:
    print(f"Error reading file: {e}")
