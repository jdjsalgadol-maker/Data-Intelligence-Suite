import os
import sys
import streamlit as st

# Forzar reconocimiento de rutas en Linux/nube
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_processor import clean_and_prepare_data, get_summaries
from modules.visuals import render_charts
from modules.storyteller import generar_narrativa
from modules.exporter import generar_pdf

st.set_page_config(page_title="Dashboard Financiero Pro", layout="wide")

st.title("🏦 Panel de Control: Análisis de Costos Bancarios")
archivo = st.file_uploader("Sube tu reporte (Excel o CSV)", type=["xlsx", "csv"])

if archivo:
    try:
        # 1. Procesamiento
        df = clean_and_prepare_data(archivo)
        bancos = sorted(df['Banco'].unique())
        seleccion = st.sidebar.multiselect("Bancos a analizar", bancos, default=bancos)
        df_filt = df[df['Banco'].isin(seleccion)]

        # 2. Cálculos y Gráficos
        df_ranking, df_mensual = get_summaries(df_filt)
        f_bar, f_pie, f_scatter, f_line = render_charts(df_filt, df_ranking, df_mensual)
        
        # 3. Generación de Storytelling
        texto_storytelling = generar_narrativa(df_filt, df_ranking, df_mensual)

        # --- INTERFAZ SUPERIOR (Métricas y Descarga) ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Gasto Neto Total", f"$ {df_filt['Costo'].sum():,.2f}")
        col2.metric("Banco más Costoso", df_ranking.iloc[0]['Banco'] if not df_ranking.empty else "N/A")
        col3.metric("Transacciones", len(df_filt))

        st.divider()

        # --- SECCIÓN DE STORYTELLING Y EXPORTACIÓN ---
        st_col_texto, st_col_pdf = st.columns([2, 1])
        
        with st_col_texto:
            st.markdown(texto_storytelling)
            
        with st_col_pdf:
            st.subheader("📥 Exportar Resultados")
            st.info("Genera un documento formal con la narrativa y la tabla de consolidación neta.")
            
            # Crear y habilitar botón de PDF
            archivo_pdf = generar_pdf(texto_storytelling, df_ranking)
            st.download_button(
                label="📄 Descargar Reporte en PDF",
                data=archivo_pdf,
                file_name="Reporte_Costos_Bancarios.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        st.divider()

        # --- SECCIÓN DE GRÁFICOS ---
        c1, c2 = st.columns(2)
        c1.plotly_chart(f_bar, use_container_width=True)
        c2.plotly_chart(f_pie, use_container_width=True)

        st.plotly_chart(f_scatter, use_container_width=True)
        st.plotly_chart(f_line, use_container_width=True)

    except Exception as e:
        st.error(f"Error en el análisis: {e}")
else:
    st.info("Por favor, sube un archivo para generar el dashboard.")
