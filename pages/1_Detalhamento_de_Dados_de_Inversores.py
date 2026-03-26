import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Detalhamento de Dados de Inversores", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #fafbfd;
        color: #1a1a2e;
    }
    h1, h2, h3 {
        color: #0f3460;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("Detalhamento de Dados de Inversores")
st.markdown("Visão global do comportamento mecânico e térmico de todos os inversores operacionais. Problemas de superaquecimento ou anomalias de tensão costumam preceder quedas de rendimento de potência.")

if 'df_inv' not in st.session_state or st.session_state.df_inv.empty:
    st.warning("Base de dados ausente. Por favor, retorne à página inicial (Análise Integrada) para inicializar a carga de dados.")
    st.stop()

df_inv = st.session_state.df_inv

# Get correct columns based on actual Excel sheet
inv_power_cols = [c for c in df_inv.columns if "PowerActive" in c]
inv_temp_cols = [c for c in df_inv.columns if "Temperature" in c]
inv_volt_cols = [c for c in df_inv.columns if "Voltage" in c]

if not inv_power_cols and not inv_temp_cols:
    st.error("Nenhum registro de Potência ou Temperatura encontrado na aba Inversores do arquivo.")
    st.stop()

# Build subplots: Power (row 1), Temperature (row 2), Voltage (row 3)
fig = make_subplots(
    rows=3, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.08,
    subplot_titles=(
        "Potência Ativa Gerada (kW)", 
        "Temperatura Interna do Inversor (°C)", 
        "Tensão Operacional (V)"
    )
)

colors = ['#E63946', '#F4A261', '#2A9D8F', '#264653', '#E9C46A', '#8AB17D', '#B5838D', '#6D6875', '#0077B6', '#90E0EF']

# 1. PowerActive
for i, col in enumerate(inv_power_cols):
    color = colors[i % len(colors)]
    inv_name = col.split(" -")[0]  # e.g., INV01
    fig.add_trace(
        go.Scatter(
            x=df_inv['sample_time'], 
            y=df_inv[col], 
            name=f"{inv_name}",
            legendgroup=inv_name,
            mode='lines',
            line=dict(width=1.5, color=color),
            hoverinfo='name+y+x'
        ),
        row=1, col=1
    )

# 2. Temperature
for i, col in enumerate(inv_temp_cols):
    color = colors[i % len(colors)]
    inv_name = col.split(" -")[0]
    fig.add_trace(
        go.Scatter(
            x=df_inv['sample_time'], 
            y=df_inv[col], 
            name=f"{inv_name}",
            legendgroup=inv_name,
            showlegend=False, # Shared legend
            mode='lines',
            line=dict(width=1.5, color=color, dash='dot'),
            hoverinfo='name+y+x'
        ),
        row=2, col=1
    )

# 3. Voltage
for i, col in enumerate(inv_volt_cols):
    color = colors[i % len(colors)]
    inv_name = col.split(" -")[0]
    fig.add_trace(
        go.Scatter(
            x=df_inv['sample_time'], 
            y=df_inv[col], 
            name=f"{inv_name}",
            legendgroup=inv_name,
            showlegend=False, # Shared legend
            mode='lines',
            line=dict(width=1.5, color=color, dash='dashdot'),
            hoverinfo='name+y+x'
        ),
        row=3, col=1
    )

fig.update_layout(
    title="Diagnóstico Tridimensional de Telemetria",
    hovermode='x unified',   
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.1,            
        xanchor="center",
        x=0.5,
        font=dict(size=12, color='#0f3460')
    ),
    height=850,
    margin=dict(l=40, r=40, t=60, b=40),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.update_traces(hoverlabel=dict(bgcolor="white", font_size=13, font_family="Segoe UI"))
fig.update_yaxes(title_text="Potência (kW)", title_font=dict(size=12), showgrid=True, gridcolor='#eef0f3', row=1, col=1)
fig.update_yaxes(title_text="Temperatura (°C)", title_font=dict(size=12), showgrid=True, gridcolor='#eef0f3', row=2, col=1)
fig.update_yaxes(title_text="Tensão (V)", title_font=dict(size=12), showgrid=True, gridcolor='#eef0f3', row=3, col=1)
fig.update_xaxes(showgrid=True, gridcolor='#eef0f3', linecolor='#cbd5e1')
fig.update_xaxes(title_text="Tempo", title_font=dict(size=12), row=3, col=1)

st.plotly_chart(fig, use_container_width=True, config={'doubleClickDelay': 1000})
st.info("💡 **Dica Analítica**: Padrões de superaquecimento ou subtensão podem preceder quedas operacionais nas curvas de Potência Ativa. Dê duplo-clique sobre a legenda de um Inversor para isolar as três curvas e averiguar as causas físicas.")
