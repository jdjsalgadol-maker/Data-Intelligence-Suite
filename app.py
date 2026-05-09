import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from fpdf import FPDF

# 1. FUNCIÓN PARA GENERAR PDF (Completa para copiar y pegar)
def generar_pdf(df, analisis_texto, escenario_plus, escenario_minus, nombre_hoja):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Reporte: {nombre_hoja}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Resumen del Analisis:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, analisis_texto)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Escenarios Proyectados:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"- Escenario Optimista (+10%): {escenario_plus:,.2f}", ln=True)
    pdf.cell(0, 10, f"- Escenario de Estres (-10%): {escenario_minus:,.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DE STREAMLIT ---
st.title("📊 Suite de Analisis Automatizado")

archivo = st.file_uploader("Sube tu archivo de Excel", type=["xlsx"])

if archivo:
    # Leer todas las pestañas
    todo_el_excel = pd.read_excel(archivo, sheet_name=None)
    nombres_pestañas = list(todo_el_excel.keys())
    
    st.sidebar.success(f"Pestañas detectadas: {len(nombres_pestañas)}")
    pestaña_elegida = st.sidebar.selectbox("Selecciona la pestaña", nombres_pestañas)
    
    df = todo_el_excel[pestaña_elegida]
    
    # Identificar columnas automáticamente
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    st.write(f"### Vista Previa: {pestaña_elegida}")
    st.dataframe(df.head())

    if not num_cols:
        st.error("Esta pestaña no tiene columnas numericas para analizar.")
    else:
        # --- FILA DE BOTONES DE ACCIÓN ---
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generar Graficos"):
                fig = px.bar(df, y=num_cols[0], title=f"Distribucion de {num_cols[0]}")
                st.plotly_chart(fig)

        with col2:
            if st.button("🔍 Identificar Patrones"):
                st.write("**Patrones detectados:**")
                st.write(f"- Valor Maximo: {df[num_cols[0]].max():,.2f}")
                st.write(f"- Valor Minimo: {df[num_cols[0]].min():,.2f}")

        with col3:
            if st.button("📝 Descripcion Analisis"):
                resumen = df[num_cols[0]].describe()
                st.write(resumen)

        # --- SECCIÓN DE ESCENARIOS Y PROYECCIONES ---
        st.write("### Escenarios y Proyecciones")
        c4, c5, c6, c7 = st.columns(4)
        val_promedio = df[num_cols[0]].mean()

        if c4.button("📉 Escenario -10%"):
            st.metric("Resultado (-10%)", f"{val_promedio * 0.9:,.2f}", "-10%")

        if c5.button("📈 Escenario +10%"):
            st.metric("Resultado (+10%)", f"{val_promedio * 1.1:,.2f}", "10%")

        if c6.button("📅 Proy. 1 Mes"):
            st.info(f"Estimado mes 1: {val_promedio * 1.05:,.2f}")

        if c7.button("📅 Proy. 12 Meses"):
            st.line_chart([val_promedio * (1.02**i) for i in range(12)])

        # --- BOTÓN DE PDF (Ahora dentro del 'if archivo') ---
        st.divider()
        st.subheader("📥 Exportar Resultados")
        
        if st.button("📄 Generar y Descargar Reporte PDF"):
            txt_reporte = f"Se analizo la pestaña '{pestaña_elegida}' con un total de {len(df)} registros."
            pdf_bytes = generar_pdf(df, txt_reporte, val_promedio*1.1, val_promedio*0.9, pestaña_elegida)
            
            st.download_button(
                label="Haga clic para descargar PDF",
                data=pdf_bytes,
                file_name=f"Reporte_{pestaña_elegida}.pdf",
                mime="application/pdf"
            )

else:
    st.info("👋 Bienvenida/o. Por favor sube un archivo Excel para comenzar el analisis.")
