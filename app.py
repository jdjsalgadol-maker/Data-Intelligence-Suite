import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la interfaz
st.set_page_config(page_title="Analizador Bancario", layout="wide")

st.title("🏦 Análisis de Costos por Entidad")
st.markdown("Carga tu reporte para analizar el comportamiento mensual de los costos.")

# Carga de archivos
archivo = st.file_uploader("Sube tu archivo (Excel o CSV)", type=["xlsx", "csv"])

if archivo:
    try:
        # Leemos el archivo
        if archivo.name.endswith('xlsx'):
            df = pd.read_excel(archivo)
        else:
            df = pd.read_csv(archivo)

        # Mapeo de columnas por posición (B=1, D=3, G=6)
        # Usamos iloc para asegurar que tomamos las columnas correctas sin importar el nombre
        analisis_df = pd.DataFrame({
            'Banco': df.iloc[:, 1],
            'Fecha': pd.to_datetime(df.iloc[:, 3]),
            'Costo': pd.to_numeric(df.iloc[:, 6], errors='coerce')
        })

        # Limpieza: eliminamos filas con datos nulos en columnas críticas
        analisis_df = analisis_df.dropna(subset=['Fecha', 'Costo'])

        # Agrupación mes a mes
        analisis_df['Mes'] = analisis_df['Fecha'].dt.to_period('M').astype(str)
        df_mensual = analisis_df.groupby(['Mes', 'Banco'])['Costo'].sum().reset_index()

        # --- Visualización ---
        st.subheader("📈 Comportamiento Mensual")
        
        # Filtro de bancos interactivo
        todos_los_bancos = df_mensual['Banco'].unique()
        seleccion = st.multiselect("Filtrar por Banco:", todos_los_bancos, default=todos_los_bancos)
        
        df_plot = df_mensual[df_mensual['Banco'].isin(seleccion)]

        if not df_plot.empty:
            fig = px.line(
                df_plot, 
                x="Mes", 
                y="Costo", 
                color="Banco",
                markers=True,
                line_shape="linear",
                labels={"Costo": "Valor Total", "Mes": "Periodo"},
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Resumen en tabla
            with st.expander("Ver tabla de datos detallada"):
                st.write(df_plot)
        else:
            st.warning("No hay datos para mostrar con los filtros seleccionados.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.info("Asegúrate de que las columnas B, D y G contengan datos válidos.")
else:
    st.info("Esperando archivo... Recuerda que la columna B debe ser el Banco, D la Fecha y G el Costo.")
