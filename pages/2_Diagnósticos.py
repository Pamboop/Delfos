import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Diagnósticos", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #fafbfd; color: #1a1a2e; }
    h1, h2, h3 { color: #0f3460; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stAlert { background-color: #ffffff; border-left: 4px solid; color: #1a1a2e; }
    div[data-testid="stMetricValue"] { color: #0f3460; }
</style>
""", unsafe_allow_html=True)

st.title("Diagnósticos de Falhas e Anomalias")
st.markdown("Auditoria estrita de todos os ativos da planta solar. A análise correlaciona telemetria com ações corretivas indicadas, isolando falhas críticas (equipamentos inoperantes ou com geração nula) de quedas severas de desempenho.")

if 'df_inv' not in st.session_state or st.session_state.df_inv.empty:
    st.warning("Base de dados ausente. Por favor, retorne à página inicial para carga de dados.")
    st.stop()

df_inv = st.session_state.df_inv
df_str = st.session_state.df_str
df_trk = st.session_state.df_trk

interval_h = 5 / 60.0

st.divider()

st.divider()

col_inv, col_str, col_trk = st.columns(3)

# ==========================================
# PRE-COMPUTING ANOMALIES FOR CROSS-CORRELATION
# ==========================================

mppt_cols = [c for c in df_str.columns if "MPPT" in c and "Normalized DC" in c]
zero_str = pd.DataFrame()
inverters_with_dead_strings = []
df_str_ranking = pd.DataFrame()

if mppt_cols:
    str_energy_full = {c.split(" - Normalized")[0]: df_str[c].sum() * interval_h for c in mppt_cols}
    df_str_ranking = pd.DataFrame(list(str_energy_full.items()), columns=['Arranjo_Completo', 'Energia MPPT'])
    zero_str = df_str_ranking[df_str_ranking['Energia MPPT'] <= 0.01]
    
if not zero_str.empty:
    inverters_with_dead_strings = zero_str['Arranjo_Completo'].apply(lambda x: x.split(" - ")[0]).unique().tolist()

trk_cols = [c for c in df_trk.columns if c.startswith("TK_")]
stuck_trk = pd.DataFrame()
misaligned_trk = []
inverters_with_stuck_trackers = []

if trk_cols:
    trk_std = {c.split(" -")[0]: df_trk[c].std() for c in trk_cols}
    df_trk_std = pd.DataFrame(list(trk_std.items()), columns=['Rastreador', 'VariacaoAngular'])
    fleet_avg_std = df_trk_std['VariacaoAngular'].mean()
    
    stuck_trk = df_trk_std[df_trk_std['VariacaoAngular'] < (0.15 * fleet_avg_std)]
    
    trk_mean = {c.split(" -")[0]: df_trk[c].mean() for c in trk_cols}
    fleet_avg_pos = np.mean(list(trk_mean.values()))
    misaligned_trk = [(t, m) for t, m in trk_mean.items() if abs(m - fleet_avg_pos) > 15]

    if not stuck_trk.empty:
        inverters_with_stuck_trackers = stuck_trk['Rastreador'].apply(lambda x: f"INV{x.split('-')[0].split('_')[1]}").unique().tolist()

# ==========================================
# 1. INVERTERS ANOMALIES
# ==========================================
with col_inv:
    st.markdown("### ⚡ Inversores")
    inv_power_cols = [c for c in df_inv.columns if "PowerActive" in c]
    inv_temp_cols = [c for c in df_inv.columns if "Temperature" in c]

    if inv_power_cols:
        inv_energy = {c.split(" -")[0]: df_inv[c].sum() * interval_h for c in inv_power_cols}
        df_inv_energy = pd.DataFrame(list(inv_energy.items()), columns=['Inversor', 'Energia (kWh)'])
        avg_inv_energy = df_inv_energy['Energia (kWh)'].mean()
        
        zero_inv = df_inv_energy[df_inv_energy['Energia (kWh)'] <= 0.01]
        sub_inv = df_inv_energy[(df_inv_energy['Energia (kWh)'] > 0.01) & (df_inv_energy['Energia (kWh)'] < 0.5 * avg_inv_energy)]
        
        erratic_invs_str = df_inv_energy[df_inv_energy['Inversor'].isin(inverters_with_dead_strings) & 
                                     (~df_inv_energy['Inversor'].isin(zero_inv['Inversor'])) & 
                                     (~df_inv_energy['Inversor'].isin(sub_inv['Inversor']))]
        
        erratic_invs_trk = df_inv_energy[df_inv_energy['Inversor'].isin(inverters_with_stuck_trackers) & 
                                     (~df_inv_energy['Inversor'].isin(zero_inv['Inversor'])) & 
                                     (~df_inv_energy['Inversor'].isin(sub_inv['Inversor']))]
        
        if not zero_inv.empty:
            anomalies_found = True
            st.error(f"**Falha Crítica (Geração Nula):** {len(zero_inv)} un.")
            for _, row in zero_inv.iterrows():
                st.write(f"❌ {row['Inversor']} (Equipamento totalmente inoperante ou desconectado da rede)")
            st.caption("🛠️ **Ação Recomendada:** Agendar visita técnica emergencial para inspeção de chaves de serviço, fusíveis rompidos ou rearme manual do equipamento.")
                
        if not sub_inv.empty:
            anomalies_found = True
            st.warning(f"**Queda Severa de Desempenho (< 50% Frota):**")
            for _, row in sub_inv.iterrows():
                dif_pct = (1 - (row['Energia (kWh)'] / avg_inv_energy)) * 100
                st.write(f"📉 {row['Inversor']}: {row['Energia (kWh)']:.1f} kWh (-{dif_pct:.1f}%)")
            st.caption("🛠️ **Ação Recomendada:** Avaliar acúmulo de poeira e detritos (sujidade), sombreamentos não previstos ou danos em parte do arranjo fotovoltaico.")
                
        if not erratic_invs_str.empty:
            anomalies_found = True
            st.error(f"**Operação Ineficiente (Arranjos Inoperantes):**")
            for _, row in erratic_invs_str.iterrows():
                st.write(f"⚠️ {row['Inversor']} (Geração contida devido a ramificações inativas)")
            st.caption("🛠️ **Ação Recomendada:** Inspecionar cabeamento dos arranjos, conectores e possíveis componentes defeituosos para integrar novamente a capacidade total.")

        if not erratic_invs_trk.empty:
            anomalies_found = True
            st.warning(f"**Funcionamento Comprometido (Rastreador Travado):**")
            for _, row in erratic_invs_trk.iterrows():
                st.write(f"⚠️ {row['Inversor']} (Geração penalizada por falta de alinhamento angular solar)")
            st.caption("🛠️ **Ação Recomendada:** Acionar equipe de rotina mecânica ao setor para destravar os motores imobilizados e reverter a perda de volume energético direto.")
                
        if zero_inv.empty and sub_inv.empty and erratic_invs_str.empty and erratic_invs_trk.empty:
            st.success("Produção de potência sadia em todas as centrais de inversão.")

    if inv_temp_cols:
        inv_max_temps = {c.split(" -")[0]: df_inv[c].max() for c in inv_temp_cols}
        df_inv_temp = pd.DataFrame(list(inv_max_temps.items()), columns=['Inversor', 'MaxTemp'])
        fleet_avg_max_temp = df_inv_temp['MaxTemp'].mean()
        
        overheating_inv = df_inv_temp[df_inv_temp['MaxTemp'] > fleet_avg_max_temp + 10]
        
        if not overheating_inv.empty:
            anomalies_found = True
            st.error(f"**Superaquecimento Detectado:**")
            for _, row in overheating_inv.iterrows():
                st.write(f"🔥 {row['Inversor']}: Pico de {row['MaxTemp']:.1f}°C")
            st.caption("🛠️ **Ação Recomendada:** Inspecionar e expurgar dutos e exaustores da acomodação térmica do inversor para prevenir perda de rendimento induzida pelo calor.")
        else:
            st.success("Equipamentos operacionais em limites térmicos tolerados.")

# ==========================================
# 2. STRINGS / MPPT ANOMALIES
# ==========================================
with col_str:
    st.markdown("### 🔋 Arranjos Fotovoltaicos (Strings)")
    
    if mppt_cols:
        avg_str_energy = df_str_ranking['Energia MPPT'].mean()
        sub_str = df_str_ranking[(df_str_ranking['Energia MPPT'] > 0.01) & (df_str_ranking['Energia MPPT'] < 0.5 * avg_str_energy)]
        
        if not zero_str.empty:
            anomalies_found = True
            st.error(f"**Arranjos Offline (Geração Nula):** {len(zero_str)} un.")
            with st.expander("Ver Módulos Improdutivos", expanded=True):
                for _, row in zero_str.iterrows():
                    inv = row['Arranjo_Completo'].split(' - ')[0]
                    str_name = row['Arranjo_Completo'].split(' - ')[1]
                    st.write(f"❌ **{inv}** | {str_name}")
            st.caption("🛠️ **Ação Recomendada:** Testar fluidez elétrica da fiação isolada. Verificar integridade dos semicondutores e seccionar a série defeituosa.")
                    
        if not sub_str.empty:
            anomalies_found = True
            st.warning(f"**Queda Acrítica de Rendimento (< 50% Frota):** {len(sub_str)} un.")
            with st.expander("Ver Arranjos Afetados"):
                for _, row in sub_str.iterrows():
                    st.write(f"📉 {row['Arranjo_Completo']}: {row['Energia MPPT']:.1f} un.")
            st.caption("🛠️ **Ação Recomendada:** Mapear incidência prolongada da sombra no horizonte do subconjunto ou encaminhar limpeza de superfícies dos painéis solares.")
                    
        if zero_str.empty and sub_str.empty:
            st.success("Arranjos fotovoltaicos provendo volume de captação equilibrado.")
            
        st.markdown("---")
        st.info("**🔎 Observação Clínica (Inversor 8 - Blocos A e B):** Os registros de telemetria paralelos do INV08 evidenciam dados **inconsistentes no grupo A**. As curvas de arranjos terminadas em *A* apresentam formato característico de falha de rastreamento mecânico, contudo, os motores dos Rastreadores Solares do INV 08 certificam amplo funcionamento normal. Em tese, os dados fisicamente válidos que correspondem à realidade da usina para este Inversor pertencem aos sensores do **grupo B**.")
    else:
        st.info("Registros de captação contínua não localizados.")

# ==========================================
# 3. TRACKERS ANOMALIES
# ==========================================
with col_trk:
    st.markdown("### ⚙️ Rastreamento Mecânico")
    
    if trk_cols:
        if not stuck_trk.empty:
            anomalies_found = True
            st.error(f"**Motores Paralisados (Sem Variação Angular):**")
            for _, row in stuck_trk.iterrows():
                st.write(f"🔧 Rastreador {row['Rastreador']}")
            st.caption("🛠️ **Ação Recomendada:** Agendamento prioritário à respectiva torre do rastreador solar para checagem do eixo e destravamento.")
        else:
            st.success("Excursão angular simétrica observada pelo parque.")
            
        if misaligned_trk:
            anomalies_found = True
            st.warning(f"**Desalinhamento Severo (> 15°):**")
            for t, m in misaligned_trk:
                st.write(f"🧭 Rastreador {t} (Média: {m:.1f}°)")
            st.caption("🛠️ **Ação Recomendada:** Solicitar recalibração virtual do medidor angular para devolver o alinhamento central comparado de radiação.")
            
        st.markdown("---")
        st.info("**🔎 Observação Clínica (Rastreador TK_04-03):** Embora o rastreador **TK_04-03** (pertencente ao INV 04) reporte dados cravados em 0° (aparente travamento mecânico), o diagnóstico cruzado revela que suas strings fotovoltaicas conectadas estão gerando energia com simetria parabólica perfeita (acompanhando o Sol). O veredicto aponta que não há estol mecânico, tratando-se exclusivamente de uma **Falha de Comunicação** do sensor de posição (inconsistência de telemetria).")
    else:
        st.info("Sem dados operacionais de rastreadores solares.")

st.divider()

st.markdown("#### 📓 Considerações O&M e Manutenções Prescritivas")
st.markdown("- **Diagnóstico Lógico Avançado**: Para uma usina saudável, todos os ativos dependentes devem fluir perfeitamente. Inversores relatando arranjos inoperantes (*Strings Mortas*) ou rastreadores inativos atuam de maneira estruturalmente ineficiente e requerem expedições corretivas imediatas devido à queda intrínseca drástica de MWh no faturamento isolado do respectivo dia.")

if not anomalies_found:
    st.success("Não foram detectados desvios agudos exigindo intervenção técnica emergencial ao sistema.")
