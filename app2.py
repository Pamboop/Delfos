import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Análise Integrada: Strings e Trackers",
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

st.title("Monitoramento Integrado: Strings & Trackers")
st.markdown("Esta visão consolida o comportamento eletromecânico do sistema, integrando a **corrente operacional das strings (eixo esquerdo)** com o **posicionamento angular dos trackers (eixo direito)**. O cruzamento destas referências permite a identificação ágil de desalinhamentos ou sombreamento excessivo.")

if df_str.empty or df_trk.empty:
    st.error("Base de dados operacionais inconsistente ou vazia após filtragem.")
    st.stop()

# --- INVERTER SELECTOR ---
inv_options = [f"Inversor {i}" for i in range(1, 10)]
selected_inv = st.selectbox("Selecione a Unidade Conversora (Inversor):", inv_options)
inv_num_str = f"{int(selected_inv.split(' ')[1]):02d}"

str_cols = [c for c in df_str.columns if c.startswith(f"INVC_{inv_num_str}_STR")]
trk_cols = [c for c in df_trk.columns if c.startswith(f"TK_{inv_num_str}")]

if not str_cols and not trk_cols:
    st.warning(f"Ausência de registros para a unidade {selected_inv}.")
    st.stop()

# --- VISUALIZATION SETUP ---
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Colors (Vibrant, Technical, Trustworthy Palette)
colors_str = ['#E63946', '#F4A261', '#2A9D8F', '#264653', '#E9C46A', '#8AB17D', '#B5838D', '#6D6875', '#0077B6', '#00B4D8', '#90E0EF', '#03045E']
for i, col in enumerate(str_cols):
    color = colors_str[i % len(colors_str)]
    str_name = col.split('_STR_')[1].split(' -')[0]
    fig.add_trace(
        go.Scatter(
            x=df_str['sample_time'], 
            y=df_str[col], 
            name=f"String {str_name}",
            mode='lines',
            line=dict(width=1.5, color=color),
            hoverinfo='name+y+x'
        ),
        secondary_y=False,
    )

colors_trk = ['#5E60CE', '#48BFE3', '#7209B7']
for i, col in enumerate(trk_cols):
    color = colors_trk[i % len(colors_trk)]
    trk_name = col.split(' -')[0]
    fig.add_trace(
        go.Scatter(
            x=df_trk['sample_time'], 
            y=df_trk[col], 
            name=f"Tracker {trk_name}",
            mode='lines',
            line=dict(width=2.5, color=color, dash='dot'),
            hoverinfo='name+y+x'
        ),
        secondary_y=True,
    )

fig.update_layout(
    title=f"Curvas Consolidadas - {selected_inv}",
    hovermode='closest',   # Evita unified tooltip para não confundir a visualização
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.25,
        xanchor="center",
        x=0.5,
        font=dict(size=13, color="#0f3460")
    ),
    height=650,
    margin=dict(l=40, r=40, t=60, b=40),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.update_yaxes(title_text="Corrente Elétrica (A) – Eixo Strings", title_font=dict(size=13, color='#E63946'), showgrid=True, gridcolor='#eef0f3', secondary_y=False)
fig.update_yaxes(title_text="Inclinação (°) – Eixo Trackers", title_font=dict(size=13, color='#5E60CE'), showgrid=False, secondary_y=True)
fig.update_xaxes(showgrid=True, gridcolor='#eef0f3', linecolor='#cbd5e1')

fig.update_traces(
    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Segoe UI")
)

st.plotly_chart(fig, use_container_width=True)
st.caption("ℹ️ **Recursos Interativos**: Clique duas vezes na legenda para focar exclusivamente em um equipamento. Um clique único (ativa/desativa) a curva. O tooltip exibirá os dados apenas do ponto sobre o qual repousa o cursor.")
