import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Financial Intelligence Dashboard", layout="wide")

# Estilos CSS para las tarjetas de métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 30px; color: #2E86C1; }
    .main { background-color: #F4F6F7; }
    div.stButton > button:first-child {
        background-color: #2E86C1; color: white; border-radius: 10px; height: 3em; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONALIDAD PDF ---
def generar_reporte_pdf(hoja, banco, stats, img_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Reporte Financiero: {banco}", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, f"Pestaña: {hoja}", ln=True, align='C')
    pdf.ln(10)
    
    if stats:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Indicadores del Periodo:", ln=True)
        pdf.set_font("Arial", '', 10)
        for k, v in stats.items():
            pdf.cell(0, 8, f"- {k.capitalize()}: {v:,.2f}", ln=True)
            
    if img_path and os.path.exists(img_path):
        pdf.ln(10)
        pdf.image(img_path, x=10, w=190)
    return pdf.output(dest='S').encode('latin-1')

# --- LÓGICA PRINCIPAL ---
st.title("🏦 Dashboard de Análisis Bancario")
archivo = st.file_uploader("Carga el archivo de movimientos bancarios", type=["xlsx"])

if archivo:
    xl = pd.ExcelFile(archivo)
    hoja_sel = st.sidebar.selectbox("Selecciona la pestaña", xl.sheet_names)
    
    # Carga de datos (Columnas B=1, D=3, G=6)
    # Nota: Usamos nombres o índices para asegurar que lea B, D y G
    df = pd.read_excel(archivo, sheet_name=hoja_sel)
    
    # Mapeo manual basado en tu descripción
    # Columna B (Banco), D (Fecha), G (Valor)
    try:
        df_final = pd.DataFrame({
            'Banco': df.iloc[:, 1],  # Columna B
            'Fecha': pd.to_datetime(df.iloc[:, 3]), # Columna D
            'Valor': pd.to_numeric(df.iloc[:, 6], errors='coerce') # Columna G
        }).dropna(subset=['Fecha', 'Valor'])
        
        # Filtro de Bancos
        lista_bancos = ["TODOS"] + sorted(df_final['Banco'].unique().tolist())
        banco_sel = st.sidebar.selectbox("Filtrar por Banco", lista_bancos)
        
        if banco_sel != "TODOS":
            df_final = df_final[df_final['Banco'] == banco_sel]

        # Procesamiento temporal para el eje X
        df_final = df_final.sort_values('Fecha')
        df_final['Periodo'] = df_final['Fecha'].dt.strftime('%Y-%m')
        df_mensual = df_final.groupby('Periodo')['Valor'].sum().reset_index()

        # --- SECCIÓN 1: KPIs ---
        st.subheader(f"Resumen Ejecutivo: {banco_sel}")
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Total Acumulado", f"$ {df_mensual['Valor'].sum():,.2f}")
        m2.metric("Promedio Mensual", f"$ {df_mensual['Valor'].mean():,.2f}")
        m3.metric("Valor Máximo", f"$ {df_mensual['Valor'].max():,.2f}")
        m4.metric("N° Operaciones", f"{len(df_final)}")

        # --- SECCIÓN 2: GRÁFICO DE TENDENCIA ---
        st.divider()
        st.subheader("Evolución Mensual y Línea de Tendencia")
        
        # Gráfico de área para estética profesional
        fig = px.area(df_mensual, x='Periodo', y='Valor', 
                      title=f"Tendencia de Movimientos - {banco_sel}",
                      labels={'Periodo': 'Año-Mes', 'Valor': 'Monto ($)'},
                      template="plotly_white",
                      color_discrete_sequence=['#AED6F1'])

        # Línea de tendencia (Regresión lineal roja)
        fig_trend = px.scatter(df_mensual, x='Periodo', y='Valor', trendline="ols")
        trendline = fig_trend.data[1]
        trendline.line.color = 'red'
        trendline.line.dash = 'dot'
        fig.add_trace(trendline)

        st.plotly_chart(fig, use_container_width=True)

        # Guardar imagen para el reporte
        fig.write_image("temp_report.png")

        # --- SECCIÓN 3: ACCIONES Y EXPORTACIÓN ---
        st.divider()
        c_acc1, c_acc2 = st.columns(2)
        
        with c_acc1:
            if st.button("📊 Analizar Patrones y Estadísticas"):
                st.write(df_mensual['Valor'].describe())
        
        with c_acc2:
            stats_dict = df_mensual['Valor'].describe().to_dict()
            pdf_bytes = generar_reporte_pdf(hoja_sel, banco_sel, stats_dict, "temp_report.png")
            st.download_button(
                label="📄 Descargar Informe Ejecutivo PDF",
                data=pdf_bytes,
                file_name=f"Reporte_{banco_sel}_{hoja_sel}.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Error al procesar las columnas B, D o G. Revisa el formato del Excel. Detalle: {e}")

else:
    st.info("👋 Sube un archivo Excel para iniciar el análisis de movimientos bancarios.")
