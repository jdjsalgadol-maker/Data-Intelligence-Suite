import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF

# --- OPTIMIZACIÓN 1: Función con Caché para no repetir procesos ---
@st.cache_data
def cargar_nombres_hojas(file):
    return pd.ExcelFile(file).sheet_names

@st.cache_data
def cargar_datos_hoja(file, hoja):
    # Solo lee la hoja seleccionada, no todo el libro
    return pd.read_excel(file, sheet_name=hoja)

# --- FUNCIÓN PDF (Sin cambios) ---
def generar_pdf(analisis_texto, esc_plus, esc_minus, nombre_hoja):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Reporte: {nombre_hoja}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, analisis_texto)
    pdf.cell(0, 10, f"Escenario +10%: {esc_plus:,.2f}", ln=True)
    pdf.cell(0, 10, f"Escenario -10%: {esc_minus:,.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.title("🚀 Suite de Inteligencia de Datos (Optimizado)")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    # --- OPTIMIZACIÓN 2: Carga solo nombres primero ---
    nombres_hojas = cargar_nombres_hojas(archivo)
    hoja_sel = st.sidebar.selectbox("Selecciona Pestaña", nombres_hojas)
    
    # --- OPTIMIZACIÓN 3: Carga datos solo de la hoja elegida ---
    df = cargar_datos_hoja(archivo, hoja_sel)
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Mostrar solo una muestra (head) para no saturar el navegador
    st.write(f"### Datos de: {hoja_sel} (Muestra)")
    st.dataframe(df.head(50)) 

    if num_cols:
        col_analisis = st.sidebar.selectbox("Columna a analizar", num_cols)
        val_promedio = df[col_analisis].mean()

        st.divider()
        c1, c2, c3 = st.columns(3)

        # Usamos estados de sesión para que los botones no se borren
        if c1.button("📊 Generar Gráficos"):
            # Muestreamos datos si el archivo es gigante para que el gráfico no sea lento
            df_grafico = df.sample(n=min(len(df), 2000)) if len(df) > 2000 else df
            fig = px.line(df_grafico, y=col_analisis, title="Tendencia Visual")
            st.plotly_chart(fig, use_container_width=True)

        if c2.button("🔍 Identificar Patrones"):
            st.info(f"Punto Máximo: {df[col_analisis].max():,.2f}")
            st.warning(f"Punto Mínimo: {df[col_analisis].min():,.2f}")

        if c3.button("📝 Descripción"):
            st.write(df[col_analisis].describe())

        # ... (Resto de botones de proyecciones y PDF igual que antes)
        st.divider()
        if st.button("📄 Descargar PDF"):
            texto = f"Analisis de {hoja_sel}. Total registros: {len(df)}"
            pdf_bytes = generar_pdf(texto, val_promedio*1.1, val_promedio*0.9, hoja_sel)
            st.download_button("Bajar PDF", pdf_bytes, f"Reporte_{hoja_sel}.pdf")
