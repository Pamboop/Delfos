import pandas as pd
from pathlib import Path

DATA_FILE = Path("C:/Users/jvict/Desktop/Pamela s2/Teste Prático - Dados para Tarefa 2 .xlsx")

try:
    xls = pd.ExcelFile(DATA_FILE)
    
    sheet_map = {name.lower(): name for name in xls.sheet_names}
    inversores_name = sheet_map.get("inverters", sheet_map.get("inversores", "Inverters"))
    strings_name = sheet_map.get("strings", "Strings")
    trackers_name = sheet_map.get("trackers", "Trackers")
    
    df_inv = pd.read_excel(xls, sheet_name=inversores_name)
    df_str = pd.read_excel(xls, sheet_name=strings_name)
    df_trk = pd.read_excel(xls, sheet_name=trackers_name)
    
    def process_df(df):
        df['sample_time'] = pd.to_datetime(df['sample_time'], errors='coerce')
        df = df.dropna(subset=['sample_time'])
        df = df[(df['sample_time'].dt.date == pd.to_datetime('2021-01-01').date()) | 
                (df['sample_time'].dt.date == pd.to_datetime('2021-01-02').date())]
        return df.sort_values('sample_time').reset_index(drop=True)
        
    df_inv = process_df(df_inv)
    df_str = process_df(df_str)
    df_trk = process_df(df_trk)

    print("DFs Loaded. Lengths: Inv", len(df_inv), "Str", len(df_str), "Trk", len(df_trk))
    
    # Let's test Resumo logic
    interval_h = 5 / 60.0
    inv_cols = [c for c in df_inv.columns if "INVC_" in c and "Active Power" in c]
    inv_energy = {c.split(" -")[0]: df_inv[c].sum() * interval_h for c in inv_cols}
    df_inv_ranking = pd.DataFrame(list(inv_energy.items()), columns=['Inversor', 'Energia (kWh)']).sort_values('Energia (kWh)', ascending=False)
    
    print("inv_ranking cols:", df_inv_ranking.columns)
    
    str_cols = [c for c in df_str.columns if "STR_" in c]
    str_energy = {c.split(" -")[0]: df_str[c].sum() * interval_h for c in str_cols}
    df_str_ranking = pd.DataFrame(list(str_energy.items()), columns=['String', 'Energia Estimada (kWh)']).sort_values('Energia Estimada (kWh)', ascending=False)
    
    print("str_ranking cols:", df_str_ranking.columns)

    def calc_availability(df, cols, threshold=0):
        total_expected = len(df)
        availabilities = []
        for c in cols:
            valid_count = df[c].dropna()[df[c] > threshold].count()
            availabilities.append({'Componente': c.split(' -')[0], 'Disponibilidade (%)': (valid_count / total_expected) * 100})
        if not availabilities:
            return pd.DataFrame(columns=['Componente', 'Disponibilidade (%)'])
        return pd.DataFrame(availabilities)

    disp_inv = calc_availability(df_inv, inv_cols, 0)
    disp_str = calc_availability(df_str, str_cols, 0)
    trk_cols = [c for c in df_trk.columns if c.startswith("TK_")]
    
    disp_trk_list = [{'Componente': c.split(' -')[0], 'Disponibilidade (%)': (df_trk[c].dropna().count() / len(df_trk)) * 100} for c in trk_cols]
    if not disp_trk_list:
        disp_trk = pd.DataFrame(columns=['Componente', 'Disponibilidade (%)'])
    else:
        disp_trk = pd.DataFrame(disp_trk_list)

    avg_disp_inv = disp_inv['Disponibilidade (%)'].mean()
    
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()

