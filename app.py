import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import os

# --- CONFIGURACIÓN Y MEMORIA (Session State) ---
if 'analisis_txt' not in st.session_state:
    st.session_state.analisis_txt = ""
if 'grafico_img' not in st.session_state:
    st.session_state.grafico_img = None

# --- FUNCIÓN MEJORADA PARA PDF ---
def generar_pdf_completo(df, titulo_hoja, metrica, resumen_stats, img_path):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Profesional
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Reporte Ejecutivo de Datos", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, f"Fuente: {titulo_hoja} | Metrica analizada: {metrica}", ln=True, align='C')
    pdf.ln(10)
    
    # Sección 1: Análisis Descriptivo
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Resumen Estadistico", ln=True)
    pdf.set_font("Arial", '', 10)
    # Convertimos el describe() a texto para el PDF
    for key, value in resumen_stats.items():
        pdf.cell(0, 8, f"- {key}: {value:,.2f}", ln=True)
    
    # Sección 2: Gráfico Visual (Si existe)
    if img_path and os.path.exists(img_path):
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "2. Analisis Visual (Tendencia)", ln=True)
        # Insertar imagen del gráfico (ajustando ancho a 150mm)
        pdf.image(img_path, x=25, y=None, w=160)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Documento generado automaticamente via Data Intelligence Suite.", align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("📊 Generador de Informes Inteligentes")

archivo = st.file_uploader("Sube tu Excel", type=["xlsx"])

if archivo:
    xl = pd.ExcelFile(archivo)
    hoja = st.sidebar.selectbox("Selecciona Pestaña", xl.sheet_names)
    df = pd.read_excel(archivo, sheet_name=hoja)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if num_cols:
        col_target = st.sidebar.selectbox("Variable Principal", num_cols)
        
        c1, c2, c3 = st.columns(3)
        
        # BOTÓN 1: GRÁFICOS (Y guardado para PDF)
        if c1.button("📊 Generar Graficos"):
            fig = px.line(df, y=col_target, title=f"Evolucion de {col_target}")
            st.plotly_chart(fig)
            # GUARDAR IMAGEN TEMPORAL PARA EL PDF
            fig.write_image("temp_chart.png")
            st.session_state.grafico_img = "temp_chart.png"
            st.success("Grafico listo para el reporte.")

        # BOTÓN 2: PATRONES / DESCRIPCIÓN
        if c2.button("📝 Descripcion Analisis"):
            stats = df[col_target].describe()
            st.write(stats)
            st.session_state.analisis_txt = stats.to_dict()
            st.success("Analisis descriptivo guardado.")

        # --- BOTÓN DE DESCARGA PDF ---
        st.divider()
        if st.button("📄 Generar Informe Final PDF"):
            if not st.session_state.analisis_txt:
                st.error("Primero haz clic en 'Descripcion Analisis' para incluir datos.")
            else:
                with st.spinner("Construyendo documento..."):
                    pdf_bytes = generar_pdf_completo(
                        df, 
                        hoja, 
                        col_target, 
                        st.session_state.analisis_txt, 
                        st.session_state.grafico_img
                    )
                    st.download_button(
                        label="⬇️ Descargar Reporte Completo",
                        data=pdf_bytes,
                        file_name=f"Reporte_{hoja}.pdf",
                        mime="application/pdf"
                    )
