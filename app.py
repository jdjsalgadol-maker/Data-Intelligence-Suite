import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Analizador de Tendencias", layout="wide")

# --- MEMORIA DE SESIÓN ---
if 'resumen_stats' not in st.session_state:
    st.session_state.resumen_stats = None
if 'img_path' not in st.session_state:
    st.session_state.img_path = None

# --- FUNCIÓN PDF ---
def exportar_pdf(hoja, resumen, img):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Reporte de Tendencia: {hoja}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Analisis Estadistico del Valor:", ln=True)
    pdf.set_font("Arial", '', 10)
    if resumen:
        for k, v in resumen.items():
            pdf.cell(0, 8, f"- {k}: {v:,.2f}", ln=True)
    
    if img and os.path.exists(img):
        pdf.ln(10)
        pdf.image(img, x=15, w=180)
        
    return pdf.output(dest='S').encode('latin-1')

st.title("📈 Análisis Automático de Valor vs Fecha")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    xl = pd.ExcelFile(archivo)
    hoja = st.sidebar.selectbox("Selecciona la pestaña", xl.sheet_names)
    df = pd.read_excel(archivo, sheet_name=hoja)

    # 1. IDENTIFICACIÓN AUTOMÁTICA RÍGIDA
    # Buscamos columnas que contengan 'fecha' y 'valor' ignorando mayúsculas
    col_fecha = next((c for c in df.columns if 'fecha' in c.lower()), None)
    col_valor = next((c for c in df.columns if 'valor' in c.lower()), None)

    if col_fecha and col_valor:
        st.sidebar.success(f"Detectado: {col_fecha} y {col_valor}")
        
        # Preprocesamiento de fechas
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        df = df.sort_values(col_fecha)
        
        # Agrupación por Año-Mes para limpiar el gráfico de líneas
        df['Año-Mes'] = df[col_fecha].dt.strftime('%Y-%m')
        df_mensual = df.groupby('Año-Mes')[col_valor].sum().reset_index()

        # --- BOTONES DE ACCIÓN ---
        c1, c2 = st.columns(2)

        with c1:
            if st.button("📈 Generar Línea de Tendencia"):
                # Gráfico de líneas con regresión lineal (OLS)
                # Usamos scatter con modo líneas para incluir la tendencia de statsmodels
                fig = px.scatter(df_mensual, x='Año-Mes', y=col_valor, 
                                 trendline="ols", 
                                 title=f"Evolución Mensual y Tendencia de {col_valor}")
                
                # Forzar que los puntos se unan con una línea
                fig.data[0].update(mode='lines+markers')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Guardar para el PDF
                fig.write_image("chart_export.png")
                st.session_state.img_path = "chart_export.png"

        with c2:
            if st.button("📝 Generar Descripción"):
                stats = df_mensual[col_valor].describe().to_dict()
                st.session_state.resumen_stats = stats
                st.write("**Estadísticas del Valor:**")
                st.write(stats)

        # --- EXPORTACIÓN ---
        st.divider()
        if st.button("📄 Descargar Reporte en PDF"):
            if st.session_state.img_path:
                pdf_bytes = exportar_pdf(hoja, st.session_state.resumen_stats, st.session_state.img_path)
                st.download_button("⬇️ Guardar PDF", pdf_bytes, f"Analisis_{hoja}.pdf")
            else:
                st.error("Primero genera el gráfico para poder exportar.")
    else:
        st.error("No se encontraron las columnas 'fecha' y 'valor' en esta pestaña.")
