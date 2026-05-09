import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from fpdf import FPDF

def generar_pdf(df, analisis_texto, escenario_plus, escenario_minus):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Reporte Inteligente de Datos", ln=True, align='C')
    pdf.ln(10)
    # ... (resto del código de la función que te pasé antes)
    return pdf.output(dest='S').encode('latin-1')
# Carga del archivo
archivo = st.file_uploader("Sube tu archivo de Excel", type=["xlsx"])

if archivo:
    # EL PARÁMETRO CLAVE: sheet_name=None
    # Esto lee TODAS las pestañas automáticamente
    todo_el_excel = pd.read_excel(archivo, sheet_name=None)
    
    # Obtenemos la lista de nombres de pestañas
    nombres_pestañas = list(todo_el_excel.keys())
    
    st.success(f"Se han detectado {len(nombres_pestañas)} pestañas.")

    # Opción A: Dejar que el usuario elija una para analizar
    pestaña_elegida = st.selectbox("¿Qué pestaña deseas analizar?", nombres_pestañas)
    
    # Extraemos solo esa pestaña para los botones de tu app
    df = todo_el_excel[pestaña_elegida]
    st.write(f"### Datos de: {pestaña_elegida}")
    st.dataframe(df.head())

    # ... (debajo de tus botones de proyecciones)

st.divider() # Una línea visual para separar
st.subheader("📥 Exportar Resultados")

if st.button("📄 Generar y Descargar Reporte PDF"):
    # 1. Calculamos los datos que irán al PDF
    val_base = df[num_cols[0]].mean()
    txt_resumen = f"Análisis de la pestaña {sheet}. Promedio actual: {val_base:,.2f}"
    
    # 2. Llamamos a la función
    pdf_bytes = generar_pdf(df, txt_resumen, val_base*1.1, val_base*0.9)
    
    # 3. Creamos el botón de descarga real
    st.download_button(
        label="Haga clic aquí para descargar PDF",
        data=pdf_bytes,
        file_name=f"Reporte_{sheet}.pdf",
        mime="application/pdf"
    )

    # Opción B: Procesamiento masivo (Ejemplo: Resumen de todas)
    if st.button("📊 Generar Resumen Global"):
        for nombre, datos in todo_el_excel.items():
            st.write(f"**Pestaña: {nombre}** - Filas: {len(datos)}")
