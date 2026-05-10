import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Financiero Pro", layout="wide")

st.title("🏦 Panel de Control: Análisis de Costos Bancarios")
st.markdown("Analiza la eficiencia y el gasto por entidad financiera.")

archivo = st.file_uploader("Sube tu reporte (Excel o CSV)", type=["xlsx", "csv"])

if archivo:
    try:
        # 1. Procesamiento de datos (B=1, D=3, G=6)
        df_raw = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
        
        df = pd.DataFrame({
            'Banco': df_raw.iloc[:, 1],
            'Fecha': pd.to_datetime(df_raw.iloc[:, 3], dayfirst=True, errors='coerce'),
            'Costo': pd.to_numeric(df_raw.iloc[:, 6], errors='coerce')
        }).dropna(subset=['Fecha', 'Costo'])

        df = df.sort_values('Fecha')
        df['Mes_Año'] = df['Fecha'].dt.strftime('%Y-%m')

        # --- FILTROS ---
        bancos = sorted(df['Banco'].unique())
        seleccion = st.sidebar.multiselect("Bancos a analizar", bancos, default=bancos)
        df_filt = df[df['Banco'].isin(seleccion)]

        # --- SECCIÓN 1: MÉTRICAS CLAVE ---
        col1, col2, col3 = st.columns(3)
        banco_top = df_filt.groupby('Banco')['Costo'].sum().idxmax()
        costo_max = df_filt.groupby('Banco')['Costo'].sum().max()
        
        col1.metric("Gasto Total", f"${df_filt['Costo'].sum():,.2f}")
        col2.metric("Banco más Costoso", banco_top)
        col3.metric("Gasto Máximo", f"${costo_max:,.2f}")

        st.divider()

        # --- SECCIÓN 2: GRÁFICOS DE COMPARACIÓN (BARRAS Y PIE) ---
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("📊 Ranking de Bancos (Costo Total)")
            df_barras = df_filt.groupby('Banco')['Costo'].sum().reset_index().sort_values('Costo', ascending=False)
            fig_bar = px.bar(
                df_barras, x='Banco', y='Costo', color='Banco',
                text_auto='.2s', title="Costo Acumulado por Entidad"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.subheader("🍰 Distribución de Gastos")
            fig_pie = px.pie(df_barras, values='Costo', names='Banco', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- SECCIÓN 3: DISPERSIÓN Y TENDENCIA ---
        st.subheader("🔍 Análisis de Dispersión y Transacciones")
        st.info("Este gráfico muestra cada transacción individual. Ayuda a identificar 'picos' o valores atípicos.")
        
        fig_scatter = px.scatter(
            df_filt, x='Fecha', y='Costo', color='Banco',
            size='Costo', hover_data=['Banco'],
            title="Dispersión de Costos por Fecha"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # --- SECCIÓN 4: COMPORTAMIENTO MENSUAL (LINEAL) ---
        st.subheader("📈 Tendencia Temporal Mes a Mes")
        df_line = df_filt.groupby(['Mes_Año', 'Banco'])['Costo'].sum().reset_index()
        fig_line = px.line(
            df_line, x='Mes_Año', y='Costo', color='Banco', markers=True,
            title="Evolución Cronológica de Costos"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    except Exception as e:
        st.error(f"Error al analizar datos: {e}")
else:
    st.info("Por favor, sube un archivo para generar el dashboard.")
