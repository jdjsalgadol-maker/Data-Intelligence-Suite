import os
import sys
import streamlit as st

# --- CONFIGURACIÓN DE RUTAS PARA STREAMLIT CLOUD ---
# Asegura que el servidor Linux encuentre la carpeta 'modules'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importación de nuestros módulos especializados
from modules.data_processor import clean_and_prepare_data, get_summaries
from modules.visuals import render_charts
from modules.storyteller import generar_narrativa
from modules.exporter import generar_pdf

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(
    page_title="Data Intelligence Suite", 
    layout="wide", 
    page_icon="🏦"
)

# Título y descripción general
st.title("🏦 Dashboard de Inteligencia Financiera")
st.markdown("""
    **Analizador de Costos Bancarios Multipestaña.** Este sistema consolida automáticamente las entidades (Columna B), 
    fechas (Columna D) y costos netos (Columna G) de todas las hojas de tu reporte para generar diagnósticos y proyecciones.
""")

# --- CARGA DE DATOS ---
archivo = st.file_uploader("📂 Sube tu reporte bancario (Excel o CSV)", type=["xlsx", "csv"])

if archivo:
    try:
        # 1. PROCESAMIENTO MODULAR (Extrae datos de todas las pestañas)
        df = clean_and_prepare_data(archivo)

        if not df.empty:
            # --- 2. BARRA LATERAL (Filtros Combinados) ---
            st.sidebar.header("⚙️ Configuración del Análisis")
            
            # Filtro A: Origen / Pestañas (Categoría)
            categorias_disponibles = sorted(df['Categoría'].unique())
            seleccion_categorias = st.sidebar.multiselect(
                "📁 Filtrar por Pestaña / Origen:", 
                options=categorias_disponibles, 
                default=categorias_disponibles
            )
            
            # Filtro B: Entidades Bancarias
            bancos_disponibles = sorted(df['Banco'].unique())
            seleccion_bancos = st.sidebar.multiselect(
                "🏦 Filtrar por Entidad:", 
                options=bancos_disponibles, 
                default=bancos_disponibles
            )
            
            # Aplicar ambos filtros cruzados
            df_filt = df[
                (df['Banco'].isin(seleccion_bancos)) & 
                (df['Categoría'].isin(seleccion_categorias))
            ]

            if not df_filt.empty:
                # 3. CÁLCULOS Y GENERACIÓN DE GRÁFICOS
                df_ranking, df_mensual = get_summaries(df_filt)
                f_bar, f_pie, f_scatter, f_line = render_charts(df_filt, df_ranking, df_mensual)
                
                # 4. STORYTELLING AUTOMÁTICO (Análisis de tendencia y proyecciones)
                texto_storytelling = generar_narrativa(df_filt, df_ranking, df_mensual)

                # --- SECCIÓN SUPERIOR: MÉTRICAS CLAVE (KPIs) ---
                col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                
                total_neto = df_filt['Costo'].sum()
                banco_lider = df_ranking.iloc[0]['Banco'] if not df_ranking.empty else "N/A"
                
                col_kpi1.metric("Gasto Neto Total", f"$ {total_neto:,.2f}")
                col_kpi2.metric("Entidad Mayoritaria", banco_lider)
                col_kpi3.metric("Movimientos Procesados", len(df_filt))

                st.divider()

                # --- SECCIÓN MEDIA: STORYTELLING Y DESCARGA DEL PDF ---
                col_story, col_pdf = st.columns([2, 1])

                with col_story:
                    st.markdown(texto_storytelling)

                with col_pdf:
                    st.subheader("📥 Generar Reporte Oficial")
                    st.info("Compila un documento formal a color con la narrativa, la tabla neta y los 4 gráficos estáticos.")
                    
                    # Empaquetamos las figuras para enviarlas al exportador PDF
                    dict_figs = {
                        "Ranking Neto Acumulado": f_bar,
                        "Distribución de Carga": f_pie,
                        "Análisis de Dispersión y Ajustes": f_scatter,
                        "Evolución y Tendencia Temporal": f_line
                    }

                    # Generación del PDF en memoria
                    with st.spinner("Procesando imágenes y diseño corporativo..."):
                        pdf_output = generar_pdf(texto_storytelling, df_ranking, dict_figs)
                    
                    st.download_button(
                        label="📄 Descargar Reporte en PDF",
                        data=pdf_output,
                        file_name=f"Reporte_Financiero_{archivo.name.split('.')[0]}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )

                st.divider()

                # --- SECCIÓN INFERIOR: VISUALIZACIÓN INTERACTIVA ---
                st.subheader("📊 Panel de Gráficos Interactivos")
                
                fila1_col1, fila1_col2 = st.columns(2)
                with fila1_col1:
                    st.plotly_chart(f_bar, use_container_width=True)
                with fila1_col2:
                    st.plotly_chart(f_pie, use_container_width=True)

                st.plotly_chart(f_scatter, use_container_width=True)
                st.plotly_chart(f_line, use_container_width=True)

            else:
                st.warning("⚠️ No hay datos para mostrar con la combinación de filtros seleccionada.")
        else:
            st.error("❌ El archivo no contiene registros válidos en las columnas requeridas (B, D y G).")

    except Exception as e:
        st.error(f"❌ Error Técnico al procesar el archivo: {e}")
        st.info("Verifica que las hojas del Excel sigan la estructura estándar.")

else:
    # Pantalla de inicio
    st.info("👋 Bienvenido. Carga tu reporte en el panel superior para procesar todas las pestañas de forma consolidada.")
