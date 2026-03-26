import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Análise Integrada: MPPT e Rastreadores",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOMIZATION (Clean & Trustworthy) ---
st.markdown("""
<style>
    .reportview-container {
        background: #f4f6f9;
    }
    .stApp {
        background-color: #fafbfd;
        color: #1a1a2e;
    }
    h1, h2, h3 {
        color: #0f3460;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stSelectbox label {
        font-weight: 600;
        color: #0f3460;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
DATA_FILE = Path("C:/Users/jvict/Desktop/Pamela s2/Teste Prático - Dados para Tarefa 2 .xlsx")

@st.cache_data(show_spinner=False)
def load_data():
    try:
        xls = pd.ExcelFile(DATA_FILE)
    except Exception as e:
        st.error(f"Erro Crítico: Inviável acessar base de dados de origem. Erro: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    sheet_map = {name.lower(): name for name in xls.sheet_names}
    inv_name = sheet_map.get("inverters", sheet_map.get("inversores", "Inverters"))
    str_name = sheet_map.get("strings", "Strings")
    trk_name = sheet_map.get("trackers", "Trackers")

    try:
        df_inv = pd.read_excel(xls, sheet_name=inv_name)
    except:
        df_inv = pd.DataFrame()
        
    try:
        df_str = pd.read_excel(xls, sheet_name=str_name)
    except:
        df_str = pd.DataFrame()
        
    try:
        df_trk = pd.read_excel(xls, sheet_name=trk_name)
    except:
        df_trk = pd.DataFrame()

    def process_df(df):
        if df.empty or 'sample_time' not in df.columns:
            return df
        
        # Format duplicated strings as physical A and B terminals
        dup_bases = [c[:-2] for c in df.columns if isinstance(c, str) and c.endswith('.1')]
        new_cols = []
        import re
        def repl(m):
            return f"MPPT {int(m.group(1)):02d} STG {int(m.group(2)):02d}"
            
        for c in df.columns:
            if not isinstance(c, str):
                new_cols.append(c)
                continue
                
            is_dup_1 = c.endswith('.1') and c[:-2] in dup_bases
            is_base = c in dup_bases

            base_c = c[:-2] if is_dup_1 else c
            parts = base_c.split(' - ')
            
            if len(parts) >= 2 and 'MPPT' in parts[1]:
                formatted = re.sub(r'MPPT(\d+)_ST[R|G](\d+)', repl, parts[1])
                if is_base:
                    parts[1] = f"{formatted} A"
                elif is_dup_1:
                    parts[1] = f"{formatted} B"
                else:
                    parts[1] = formatted
                new_cols.append(' - '.join(parts))
            else:
                if is_base: new_cols.append(base_c + " A")
                elif is_dup_1: new_cols.append(base_c + " B")
                else: new_cols.append(c)
                
        df.columns = new_cols
        
        df['sample_time'] = pd.to_datetime(df['sample_time'], errors='coerce')
        df = df.dropna(subset=['sample_time'])
        df = df[(df['sample_time'].dt.date == pd.to_datetime('2021-01-01').date()) | 
                (df['sample_time'].dt.date == pd.to_datetime('2021-01-02').date())]
        return df.sort_values('sample_time').reset_index(drop=True)

    return process_df(df_inv), process_df(df_str), process_df(df_trk)

with st.spinner("Processamento Analítico em Andamento..."):
    if 'df_inv' not in st.session_state:
        df_i, df_s, df_t = load_data()
        st.session_state.df_inv = df_i
        st.session_state.df_str = df_s
        st.session_state.df_trk = df_t

df_inv = st.session_state.df_inv
df_str = st.session_state.df_str
df_trk = st.session_state.df_trk

st.title("Monitoramento Integrado: MPPT & Rastreadores Solares")
st.markdown("Esta visão consolida o comportamento do sistema cruzando a **posição angular dos rastreadores (eixo esquerdo)** com o **desempenho de Potência Contínua Normalizada do MPPT (eixo direito)**. As medições estão unificadas ao eixo temporal comum das medições, permitindo aferição do efeito exato do rastreamento na variação de potência normalizada.")

if df_str.empty or df_trk.empty:
    st.error("Base de dados operacionais inconsistente ou vazia após filtragem.")
    st.stop()

# --- INVERTER SELECTOR ---
inv_options = [f"Inversor {i}" for i in range(1, 10)]
selected_inv = st.selectbox("Selecione a Unidade Conversora (Inversor):", inv_options)
inv_num_str = f"{int(selected_inv.split(' ')[1]):02d}"

# Fetch MPPT Normalized DC columns from Strings
# Their format is: INV01 - MPPT1_STR01 - Normalized DC Power
mppt_cols = [c for c in df_str.columns if c.startswith(f"INV{inv_num_str} - MPPT") and "Normalized DC" in c]
trk_cols = [c for c in df_trk.columns if c.startswith(f"TK_{inv_num_str}")]

if not mppt_cols and not trk_cols:
    st.warning(f"Ausência de registros MPPT ou Rastreadores Solares para a unidade {selected_inv}.")
    st.stop()

# --- VISUALIZATION SETUP ---
fig = make_subplots(
    rows=2, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.08,
    subplot_titles=(f"Curvas MPPT (Potência Contínua Normalizada)", f"Posição Angular dos Rastreadores Solares (°)")
)

# 1. Add MPPT to Top Plot (row=1, col=1)
colors_mppt = ['#E63946', '#F4A261', '#2A9D8F', '#264653', '#E9C46A', '#8AB17D', '#B5838D', '#6D6875', '#0077B6', '#00B4D8', '#90E0EF', '#03045E']
for i, col in enumerate(mppt_cols):
    color = colors_mppt[i % len(colors_mppt)]
    mppt_name = col.split(' - ')[1]
    fig.add_trace(
        go.Scatter(
            x=df_str['sample_time'], 
            y=df_str[col], 
            name=f"{mppt_name}",
            mode='lines',
            line=dict(width=1.5, color=color),
            hoverinfo='name+y+x'
        ),
        row=1, col=1
    )

# 2. Add Trackers to Bottom Plot (row=2, col=1)
colors_trk = ['#5E60CE', '#48BFE3', '#7209B7']
for i, col in enumerate(trk_cols):
    color = colors_trk[i % len(colors_trk)]
    trk_name = col.split(' -')[0]
    fig.add_trace(
        go.Scatter(
            x=df_trk['sample_time'], 
            y=df_trk[col], 
            name=f"Rastreador {trk_name}",
            mode='lines',
            line=dict(width=2.5, color=color, dash='dot'),
            hoverinfo='name+y+x'
        ),
        row=2, col=1
    )


fig.update_layout(
    title=f"Rendimento MPPT vs Posição Mecânica - {selected_inv}",
    hovermode='x unified',   
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.15,
        xanchor="center",
        x=0.5,
        font=dict(size=13, color="#0f3460")
    ),
    height=800,  # Aumentado para acomodar 2 gráficos confortavelmente
    margin=dict(l=40, r=40, t=80, b=40),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.update_yaxes(title_text="Energia MPPT", title_font=dict(size=12, color='#E63946'), showgrid=True, gridcolor='#eef0f3', row=1, col=1)
fig.update_yaxes(title_text="Posição (°)", title_font=dict(size=12, color='#5E60CE'), showgrid=True, gridcolor='#eef0f3', row=2, col=1)
fig.update_xaxes(showgrid=True, gridcolor='#eef0f3', linecolor='#cbd5e1')
fig.update_xaxes(title_text="Data / Hora", row=2, col=1)

fig.update_traces(
    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Segoe UI")
)

# Aumentando doubleClickDelay para 1000ms (1 segundo) para facilitar o isolamento
st.plotly_chart(fig, use_container_width=True, config={'doubleClickDelay': 1000})
st.caption("ℹ️ **Recursos Interativos**: Clique duplo atua isolando um rastreamento de curva. Para habilitar e desabilitar um único módulo de MPPT, opere cliques simples sobre a legenda associada.")
