import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import os

# --- CONFIGURACIÓN DE SESIÓN ---
if 'analisis_resultado' not in st.session_state:
    st.session_state.analisis_resultado = "Aún no se ha generado un análisis."
if 'grafico_guardado' not in st.session_state:
    st.session_state.grafico_guardado = None

# --- FUNCIÓN DE PDF MEJORADA ---
def crear_pdf(hoja, metrica, resumen_dict, img_path):
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Reporte de Tendencias e Inteligencia", ln=True, align='C')
    pdf.ln(5)
    
    # Información General
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Pestaña analizada: {hoja}", ln=True)
    pdf.cell(0, 10, f"Métrica principal: {metrica}", ln=True)
    pdf.ln(5)
    
    # Datos Estadísticos
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Resumen Estadistico:", ln=True)
    pdf.set_font("Arial", '', 10)
    if isinstance(resumen_dict, dict):
        for k, v in resumen_dict.items():
            pdf.cell(0, 8, f"- {k}: {v:,.2f}", ln=True)
    
    # Gráfico de Tendencia
    if img_path and os.path.exists(img_path):
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "2. Grafico de Tendencia Temporal (Año-Mes):", ln=True)
        pdf.image(img_path, x=15, y=None, w=180)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("📊 Analizador de Tendencias Temporales")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    xl = pd.ExcelFile(archivo)
    hoja = st.sidebar.selectbox("Selecciona Pestaña", xl.sheet_names)
    
    # Carga de datos
    df = pd.read_excel(archivo, sheet_name=hoja)
    
    # Identificar fechas y números
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except: pass
            
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if date_cols and num_cols:
        col_fecha = st.sidebar.selectbox("Columna de Tiempo", date_cols)
        col_valor = st.sidebar.selectbox("Columna de Valor", num_cols)

        # PREPROCESAMIENTO: Ordenar y formatear Eje X (Año-Mes)
        df = df.sort_values(col_fecha)
        df['Periodo'] = df[col_fecha].dt.strftime('%Y-%m') # Formato: 2024-01, 2024-02...
        
        # Agrupar por mes para que la línea de tendencia sea clara
        df_mensual = df.groupby('Periodo')[col_valor].sum().reset_index()

        st.write(f"### Análisis de {col_valor} por {col_fecha}")
        st.dataframe(df_mensual.head())

        col_btn1, col_btn2 = st.columns(2)

        # BOTÓN 1: GRÁFICO CON LÍNEA DE TENDENCIA
        if col_btn1.button("📈 Generar Grafico de Tendencia"):
            # Creamos el gráfico con línea de tendencia (OLS)
            # Usamos scatter + trendline para que Plotly dibuje la regresión
            fig = px.scatter(df_mensual, x='Periodo', y=col_valor, 
                             trendline="ols", 
                             title=f"Tendencia Temporal: {col_valor}",
                             labels={'Periodo': 'Año-Mes', col_valor: 'Total'})
            
            # Convertimos los puntos en una línea continua para mejor visualización
            fig.data[0].update(mode='lines+markers') 
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Guardar imagen para el PDF
            fig.write_image("tendencia_temp.png")
            st.session_state.grafico_guardado = "tendencia_temp.png"
            st.success("Gráfico de tendencia generado y guardado para el reporte.")

        # BOTÓN 2: DESCRIPCIÓN
        if col_btn2.button("📝 Descripción Analisis"):
            stats = df_mensual[col_valor].describe().to_dict()
            st.session_state.analisis_resultado = stats
            st.write("**Resumen Estadístico Mensual:**")
            st.write(stats)

        # --- EXPORTACIÓN ---
        st.divider()
        if st.button("📄 Descargar Informe Final PDF"):
            if st.session_state.grafico_guardado:
                pdf_bytes = crear_pdf(
                    hoja, 
                    col_valor, 
                    st.session_state.analisis_resultado, 
                    st.session_state.grafico_guardado
                )
                st.download_button(
                    label="⬇️ Descargar Reporte PDF",
                    data=pdf_bytes,
                    file_name=f"Analisis_Tendencia_{hoja}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Primero genera el gráfico para poder incluirlo en el PDF.")
    else:
        st.warning("El archivo necesita al menos una columna de fecha y una de valor.")
