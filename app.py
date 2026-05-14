import os
import sys
import streamlit as st

# --- CONFIGURACION DE RUTAS PARA STREAMLIT CLOUD ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importacion de modulos especializados
from modules.data_processor import clean_and_prepare_data, get_summaries
from modules.visuals import render_charts
from modules.storyteller import generar_narrativa
from modules.exporter import generar_pdf

# --- CONFIGURACION DE LA INTERFAZ ---
st.set_page_config(
    page_title="Data Intelligence Suite", 
    layout="wide", 
    page_icon="banking"
)

# --- FUNCION DE CACHE PARA EL PDF ---
# Esta funcion evita que el PDF se regenere innecesariamente
@st.cache_data(show_spinner=False)
def obtener_pdf_optimizado(texto, ranking, figs):
    return generar_pdf(texto, ranking, figs)

# Titulo y descripcion
st.title("Data Intelligence Suite")
st.markdown("Analizador de Costos Bancarios Multipestana.")

archivo = st.file_uploader("Subir reporte (Excel o CSV)", type=["xlsx", "csv"])

if archivo:
    try:
        df = clean_and_prepare_data(archivo)

        if not df.empty:
            # --- FILTROS ---
            st.sidebar.header("Configuracion")
            
            cats = sorted(df['Categoria'].unique())
            sel_cats = st.sidebar.multiselect("Filtrar por Pestana:", options=cats, default=cats)
            
            bancos = sorted(df['Banco'].unique())
            sel_bancos = st.sidebar.multiselect("Filtrar por Entidad:", options=bancos, default=bancos)
            
            df_filt = df[(df['Banco'].isin(sel_bancos)) & (df['Categoria'].isin(sel_cats))]

            if not df_filt.empty:
                # 1. CALCULOS
                df_ranking, df_mensual = get_summaries(df_filt)
                f_bar, f_pie, f_proy, f_line = render_charts(df_filt, df_ranking, df_mensual)
                texto_storytelling = generar_narrativa(df_filt, df_ranking, df_mensual)

                # 2. METRICAS
                c1, c2, c3 = st.columns(3)
                c1.metric("Gasto Neto Total", f"$ {df_filt['Costo'].sum():,.2f}")
                c2.metric("Entidad Mayoritaria", df_ranking.iloc[0]['Banco'] if not df_ranking.empty else "N/A")
                c3.metric("Registros", len(df_filt))

                st.divider()

                # 3. STORYTELLING Y PDF
                col_story, col_pdf = st.columns([2, 1])

                with col_story:
                    st.markdown(texto_storytelling)

                with col_pdf:
                    st.subheader("Reporte Oficial")
                    
                    dict_figs = {
                        "Ranking": f_bar,
                        "Participacion": f_pie,
                        "Proyeccion": f_proy,
                        "Tendencia": f_line
                    }

                    # Generamos el PDF usando el Cache
                    with st.spinner("Preparando documento..."):
                        pdf_output = obtener_pdf_optimizado(texto_storytelling, df_ranking, dict_figs)
                    
                    st.download_button(
                        label="Descargar Reporte en PDF",
                        data=pdf_output,
                        file_name=f"Reporte_{archivo.name.split('.')[0]}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )

                st.divider()

                # 4. GRAFICOS
                st.subheader("Panel Interactivo")
                f1, f2 = st.columns(2)
                f1.plotly_chart(f_bar, use_container_width=True)
                f2.plotly_chart(f_pie, use_container_width=True)
                st.plotly_chart(f_proy, use_container_width=True)
                st.plotly_chart(f_line, use_container_width=True)

            else:
                st.warning("No hay datos para la seleccion.")
        else:
            st.error("Archivo sin registros validos.")

    except Exception as e:
        st.error(f"Error: {e}")
