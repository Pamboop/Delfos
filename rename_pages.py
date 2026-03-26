import os
from pathlib import Path

base_dir = Path("c:/Users/jvict/Desktop/Pamela s2/pages")

old_inv = base_dir / "1_Diagnostico_Inversores.py"
new_inv = base_dir / "1_Detalhamento_de_Dados_de_Inversores.py"

old_res = base_dir / "2_Resumo_Executivo.py"
new_res = base_dir / "2_Diagnósticos.py"

if old_inv.exists():
    os.rename(old_inv, new_inv)
    print("Renamed inverter page")

if old_res.exists():
    os.rename(old_res, new_res)
    print("Renamed resumo page")
