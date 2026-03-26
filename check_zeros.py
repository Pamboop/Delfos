import pandas as pd
from pathlib import Path

DATA_FILE = Path("C:/Users/jvict/Desktop/Pamela s2/Teste Prático - Dados para Tarefa 2 .xlsx")

xls = pd.ExcelFile(DATA_FILE)
sheet_map = {name.lower(): name for name in xls.sheet_names}
inv_name = sheet_map.get("inverters", "Inverters")
str_name = sheet_map.get("strings", "Strings")

df_inv = pd.read_excel(xls, sheet_name=inv_name)
df_str = pd.read_excel(xls, sheet_name=str_name)

df_inv['sample_time'] = pd.to_datetime(df_inv['sample_time'], errors='coerce')
df_inv = df_inv.dropna(subset=['sample_time'])
df_inv = df_inv[(df_inv['sample_time'].dt.date == pd.to_datetime('2021-01-01').date()) | 
        (df_inv['sample_time'].dt.date == pd.to_datetime('2021-01-02').date())]

df_str['sample_time'] = pd.to_datetime(df_str['sample_time'], errors='coerce')
df_str = df_str.dropna(subset=['sample_time'])
df_str = df_str[(df_str['sample_time'].dt.date == pd.to_datetime('2021-01-01').date()) | 
        (df_str['sample_time'].dt.date == pd.to_datetime('2021-01-02').date())]

interval_h = 5 / 60.0

print("--- INVERTERS (PowerActive) ---")
inv_cols = [c for c in df_inv.columns if "PowerActive" in c]
for c in inv_cols:
    total = df_inv[c].sum() * interval_h
    if total <= 0.1:
        print(f"ZERO/LOW Generation Inverter: {c} -> {total}")

print("\n--- MPPT STRINGS (Normalized DC Power) ---")
mppt_cols = [c for c in df_str.columns if "MPPT" in c and "Normalized DC" in c]
zero_strings = []
for c in mppt_cols:
    total = df_str[c].sum() * interval_h
    if total <= 0.1:
        zero_strings.append((c, total))

print(f"Total zero/low MPPT strings: {len(zero_strings)}")
for c, t in zero_strings:
    print(f"{c} -> {t}")
