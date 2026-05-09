import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Analítico", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS (Para las tarjetas de métricas) ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1f77b4; }
    .main { background-color: #f8f9fa; }
    div.stButton > button:first-child {
        background-color: #007bff; color: white; border-radius: 8px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN ---
if 'pdf_content' not in st.session_state:
    st.session_state.pdf_content = {"stats": None, "img": None}

def exportar_pdf(hoja, resumen, img):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Dashboard Analitico - Reporte: {hoja}", ln=True, align='C')
    pdf.ln(10)
    if resumen:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Indicadores Clave:", ln=True)
        pdf.set_font("Arial", '', 10)
        for k, v in resumen.items():
            pdf.cell(0, 8, f"- {k.capitalize()}: {v:,.2f}", ln=True)
    if img and os.path.exists(img):
        pdf.ln(5)
        pdf.image(img, x=10, w=190)
    return pdf.output(dest='S').encode('latin-1')

# --- HEADER ---
st.title("📊 Dashboard Analítico")
st.caption("Visualización de Datos y Análisis de Tendencias Temporales")

archivo = st.file_uploader("Carga tu archivo Excel", type=["xlsx"])

if archivo:
    xl = pd.ExcelFile(archivo)
    hoja = st.sidebar.selectbox("Selecciona la pestaña", xl.sheet_names)
    df = pd.read_excel(archivo, sheet_name=hoja)

    # Identificación automática de columnas (ignora mayúsculas/minúsculas)
    df.columns = [c.lower().strip() for c in df.columns]
    col_fecha = next((c for c in df.columns if 'fecha' in c), None)
    col_valor = next((c for c in df.columns if any(x in c for x in ['abono', 'valor', 'cargo', 'saldo'])), None)

    if col_fecha and col_valor:
        # Procesamiento de Datos
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        df = df.sort_values(col_fecha)
        df['año-mes'] = df[col_fecha].dt.strftime('%Y-%m')
        df_mensual = df.groupby('año-mes')[col_valor].sum().reset_index()

        # --- SECCIÓN 1: KPI CARDS (Como en tu imagen) ---
        st.write("---")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        max_val = df_mensual[col_valor].max()
        min_val = df_mensual[col_valor].min()
        promedio = df_mensual[col_valor].mean()
        total_acum = df_mensual[col_valor].sum()

        kpi1.metric("Valor Máximo", f"{max_val:,.2f}", "Pico")
        kpi2.metric("Valor Mínimo", f"{min_val:,.2f}", "Suelo", delta_color="inverse")
        kpi3.metric("Promedio Mensual", f"{promedio:,.2f}")
        kpi4.metric("Total Acumulado", f"{total_acum:,.2f}")
        st.write("---")

        # --- SECCIÓN 2: GRÁFICO DE ÁREA Y TENDENCIA ---
        st.subheader(f"Evolución Temporal de {col_valor.capitalize()}")
        
        # Gráfico de área para mayor impacto visual
        fig = px.area(df_mensual, x='año-mes', y=col_valor, 
                      title="Tendencia Mensual con Regresión Lineal",
                      labels={'año-mes': 'Periodo', col_valor: 'Monto'},
                      template="plotly_white")
        
        # Añadir línea de tendencia matemática (Regresión OLS)
        fig_trend = px.scatter(df_mensual, x='año-mes', y=col_valor, trendline="ols")
        trendline_data = fig_trend.data[1]
        trendline_data.line.color = 'red' # Color de la tendencia
        fig.add_trace(trendline_data)

        st.plotly_chart(fig, use_container_width=True)

        # Guardar imagen para el PDF
        fig.write_image("dash_report.png")
        st.session_state.pdf_content["img"] = "dash_report.png"

        # --- SECCIÓN 3: ACCIONES ---
        c1, c2, c3 = st.columns(3)
        
        with c1:
            if st.button("📝 Generar Análisis"):
                stats = df_mensual[col_valor].describe().to_dict()
                st.session_state.pdf_content["stats"] = stats
                st.write("**Resumen Estadístico:**")
                st.json(stats)

        with c2:
            if st.button("📄 Exportar a PDF"):
                if st.session_state.pdf_content["img"]:
                    pdf_bytes = exportar_pdf(hoja, st.session_state.pdf_content["stats"], st.session_state.pdf_content["img"])
                    st.download_button("⬇️ Descargar Reporte PDF", pdf_bytes, f"Dashboard_{hoja}.pdf")
                else:
                    st.error("Error al generar imagen.")

        with c3:
            # Opción para ver los datos crudos
            if st.checkbox("Ver Tabla de Datos"):
                st.dataframe(df_mensual, use_container_width=True)

    else:
        st.error("No se encontraron columnas de 'fecha' y 'valor/abono' en esta pestaña.")
else:
    st.info("👋 Por favor, carga un archivo Excel para visualizar el Dashboard Analítico.")
