import os
import sys
import streamlit as st

# --- CONFIGURACIÓN DE RUTAS PARA STREAMLIT CLOUD ---
# Esto asegura que la nube encuentre la carpeta 'modules'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importación de nuestros módulos especializados
from modules.data_processor import clean_and_prepare_data, get_summaries
from modules.visuals import render_charts
from modules.storyteller import generar_narrativa
from modules.exporter import generar_pdf

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(
    page_title="Data Intelligence Suite - BitCriollo", 
    layout="wide", 
    page_icon="🏦"
)

# Estilo personalizado para el título
st.title("🏦 Dashboard de Inteligencia Financiera")
st.markdown("""
    **Analizador de Costos Bancarios Profundo.** Este sistema procesa automáticamente las entidades (B), fechas (D) y costos netos (G) 
    para generar diagnósticos de tendencia y reportes ejecutivos.
""")

# --- CARGA DE DATOS ---
archivo = st.file_uploader("📂 Sube tu reporte bancario (Excel o CSV)", type=["xlsx", "csv"])

if archivo:
    try:
        # 1. PROCESAMIENTO (Módulo Data Processor)
        # Limpia datos, maneja negativos y prepara la serie de tiempo
        df = clean_and_prepare_data(archivo)

        # 2. SEGMENTACIÓN / FILTROS (Barra Lateral)
        st.sidebar.header("⚙️ Configuración del Análisis")
        bancos_disponibles = sorted(df['Banco'].unique())
        seleccion_bancos = st.sidebar.multiselect(
            "Selecciona Entidades:", 
            options=bancos_disponibles, 
            default=bancos_disponibles
        )
        
        # Aplicar filtro de usuario
        df_filt = df[df['Banco'].isin(seleccion_bancos)]

        if not df_filt.empty:
            # 3. CÁLCULOS Y GENERACIÓN DE GRÁFICOS
            df_ranking, df_mensual = get_summaries(df_filt)
            f_bar, f_pie, f_scatter, f_line = render_charts(df_filt, df_ranking, df_mensual)
            
            # 4. GENERACIÓN DE STORYTELLING (Análisis de tendencia y proyecciones)
            texto_storytelling = generar_narrativa(df_filt, df_ranking, df_mensual)

            # --- SECCIÓN A: MÉTRICAS CLAVE (KPIs) ---
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            
            total_neto = df_filt['Costo'].sum()
            banco_lider = df_ranking.iloc[0]['Banco'] if not df_ranking.empty else "N/A"
            
            col_kpi1.metric("Gasto Neto Total", f"$ {total_neto:,.2f}")
            col_kpi2.metric("Entidad Mayoritaria", banco_lider)
            col_kpi3.metric("Volumen de Registros", len(df_filt))

            st.divider()

            # --- SECCIÓN B: STORYTELLING Y EXPORTACIÓN ---
            col_story, col_pdf = st.columns([2, 1])

            with col_story:
                st.markdown(texto_storytelling)

            with col_pdf:
                st.subheader("📥 Generar Reporte Oficial")
                st.info("El PDF incluirá la narrativa completa, los 4 gráficos analíticos y la tabla de saldos netos.")
                
                # Diccionario para enviar los gráficos al generador de PDF
                dict_figs = {
                    "Ranking de Costos": f_bar,
                    "Participación": f_pie,
                    "Dispersión y Picos": f_scatter,
                    "Línea de Tendencia": f_line
                }

                # Generación del archivo PDF (Módulo Exporter)
                with st.spinner("Compilando gráficos y narrativa..."):
                    pdf_output = generar_pdf(texto_storytelling, df_ranking, dict_figs)
                
                st.download_button(
                    label="📄 Descargar Reporte en PDF",
                    data=pdf_output,
                    file_name=f"Reporte_Financiero_{archivo.name}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )

            st.divider()

            # --- SECCIÓN C: DASHBOARD VISUAL ---
            st.subheader("📊 Visualización de Comportamientos")
            
            fila1_col1, fila1_col2 = st.columns(2)
            with fila1_col1:
                st.plotly_chart(f_bar, use_container_width=True)
            with fila1_col2:
                st.plotly_chart(f_pie, use_container_width=True)

            st.plotly_chart(f_scatter, use_container_width=True)
            st.plotly_chart(f_line, use_container_width=True)

        else:
            st.warning("Selecciona al menos un banco en la barra lateral para ver los resultados.")

    except Exception as e:
        st.error(f"❌ Error Crítico en el Análisis: {e}")
        st.info("Asegúrate de que la columna B tenga Bancos, la D Fechas y la G Valores Numéricos.")

else:
    # Pantalla de bienvenida cuando no hay archivo
    st.info("👋 Bienvenido. Por favor, carga un archivo Excel o CSV para comenzar el análisis.")
    st.image("https://images.unsplash.com/photo-1551288049-bbbda3e66f71?auto=format&fit=crop&q=80&w=1000", caption="Análisis Modular de Datos Bancarios")
