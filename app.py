import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

st.set_page_config(page_title="Analizador Inteligente", layout="wide")

# Estilo para los botones
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>""", unsafe_allow_html=True)

st.title("🚀 Data Intelligence Suite")
st.sidebar.header("Carga de Información")

archivo = st.sidebar.file_uploader("Sube tu reporte (Excel/CSV)", type=["xlsx", "csv"])

if archivo:
    # Carga automática de pestañas
    if archivo.name.endswith('xlsx'):
        dict_hojas = pd.read_excel(archivo, sheet_name=None)
        hoja = st.sidebar.selectbox("Selecciona Pestaña", list(dict_hojas.keys()))
        df = dict_hojas[hoja]
    else:
        df = pd.read_csv(archivo)

    # Identificación automática de tipos
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except: pass
    
    fechas = df.select_dtypes(include=['datetime64']).columns.tolist()
    numeros = df.select_dtypes(include=[np.number]).columns.tolist()

    if fechas and numeros:
        target_f = fechas[0]
        target_v = numeros[0]
        df = df.sort_values(target_f)

        # GRID DE BOTONES PRINCIPALES
        st.write("### Panel de Control de Análisis")
        c1, c2, c3 = st.columns(3)
        c4, c5 = st.columns(2)
        c6, c7 = st.columns(2)

        # 1. Generar Gráficos
        if c1.button("📊 Generar Gráficos"):
            st.subheader("Visualización Dinámica")
            fig = px.area(df, x=target_f, y=target_v, title=f"Evolución de {target_v}")
            st.plotly_chart(fig, use_container_width=True)

        # 2. Identificar Patrones
        if c2.button("🔍 Identificar Patrones"):
            st.subheader("Detección de Patrones")
            df['Mes'] = df[target_f].dt.month
            estacionalidad = df.groupby('Mes')[target_v].mean()
            fig_p = px.bar(estacionalidad, title="Comportamiento Promedio por Mes")
            st.plotly_chart(fig_p)

        # 3. Descripción Análisis (Texto)
        if c3.button("📝 Descripción de Datos"):
            st.subheader("Resumen Ejecutivo")
            total = df[target_v].sum()
            promedio = df[target_v].mean()
            st.write(f"El análisis de la columna **{target_v}** muestra un volumen total de **{total:,.2f}** con un promedio transaccional de **{promedio:,.2f}**.")

        # 4 y 5. Escenarios
        promedio_act = df[target_v].mean()
        if c4.button("📉 Escenario -10%"):
            st.warning(f"Resultado bajo escenario de estrés (-10%): **{promedio_act * 0.90:,.2f}**")
            
        if c5.button("📈 Escenario +10%"):
            st.success(f"Resultado bajo escenario optimista (+10%): **{promedio_act * 1.10:,.2f}**")

        # 6 y 7. Proyecciones
        def forecast_func(periods):
            model = SimpleExpSmoothing(df[target_v]).fit()
            return model.forecast(periods)

        if c6.button("📅 Proyección 1 Mes"):
            f_1 = forecast_func(1)
            st.metric("Estimado Próximo Mes", f"{f_1.iloc[0]:,.2f}")

        if c7.button("📅 Proyección 12 Meses"):
            f_12 = forecast_func(12)
            st.line_chart(f_12)
            st.write("Tendencia proyectada para el próximo año fiscal.")

    else:
        st.info("El archivo debe contener al menos una columna de fecha y una numérica.")
else:
    st.info("Esperando archivo para procesar indicadores...")
