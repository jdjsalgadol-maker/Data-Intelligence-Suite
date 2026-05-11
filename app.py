import os
import sys
import streamlit as st

# Forzar al servidor de la nube a reconocer la carpeta actual
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_processor import clean_and_prepare_data, get_summaries
from modules.visuals import render_charts

st.set_page_config(page_title="Dashboard Financiero Pro", layout="wide")

st.title("🏦 Panel de Control: Análisis de Costos Bancarios")
archivo = st.file_uploader("Sube tu reporte (Excel o CSV)", type=["xlsx", "csv"])

if archivo:
    try:
        # 1. Procesamiento Modular
        df = clean_and_prepare_data(archivo)

        # 2. Filtros
        bancos = sorted(df['Banco'].unique())
        seleccion = st.sidebar.multiselect("Bancos a analizar", bancos, default=bancos)
        df_filt = df[df['Banco'].isin(seleccion)]

        # 3. Cálculos y Gráficos
        df_ranking, df_mensual = get_summaries(df_filt)
        f_bar, f_pie, f_scatter, f_line = render_charts(df_filt, df_ranking, df_mensual)

        # --- Interfaz de Usuario ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Gasto Total", f"${df_filt['Costo'].sum():,.2f}")
        col2.metric("Banco más Costoso", df_ranking.iloc[0]['Banco'] if not df_ranking.empty else "N/A")
        col3.metric("Transacciones", len(df_filt))

        st.divider()

        c1, c2 = st.columns(2)
        c1.plotly_chart(f_bar, use_container_width=True)
        c2.plotly_chart(f_pie, use_container_width=True)

        st.plotly_chart(f_scatter, use_container_width=True)
        st.plotly_chart(f_line, use_container_width=True)

    except Exception as e:
        st.error(f"Error en el análisis: {e}")
else:
    st.info("Por favor, sube un archivo para generar el dashboard.")
