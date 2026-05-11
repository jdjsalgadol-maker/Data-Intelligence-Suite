import pandas as pd

def clean_and_prepare_data(archivo):
    """Carga y consolida las columnas B, D y G de TODAS las pestañas del Excel."""
    
    if archivo.name.endswith('xlsx'):
        # sheet_name=None captura todas las pestañas en un diccionario
        diccionario_hojas = pd.read_excel(archivo, sheet_name=None)
        lista_tablas = []
        
        # Iteramos por cada pestaña encontrada
        for nombre_pestaña, df_raw in diccionario_hojas.items():
            # Validamos que la hoja tenga datos suficientes para llegar a la columna G (índice 6)
            if df_raw.shape[1] > 6:
                df_temp = pd.DataFrame({
                    'Banco': df_raw.iloc[:, 1],
                    'Fecha': pd.to_datetime(df_raw.iloc[:, 3], dayfirst=True, errors='coerce'),
                    'Costo': pd.to_numeric(df_raw.iloc[:, 6], errors='coerce'),
                    'Categoría': nombre_pestaña  # 💡 Inyectamos el nombre de la pestaña como dato
                }).dropna(subset=['Fecha', 'Costo'])
                
                lista_tablas.append(df_temp)
        
        # Unimos todas las pestañas procesadas una debajo de la otra
        df = pd.concat(lista_tablas, ignore_index=True) if lista_tablas else pd.DataFrame()

    else:
        # Si el usuario sube un CSV, se procesa normal (los CSV no tienen pestañas)
        df_raw = pd.read_csv(archivo)
        df = pd.DataFrame({
            'Banco': df_raw.iloc[:, 1],
            'Fecha': pd.to_datetime(df_raw.iloc[:, 3], dayfirst=True, errors='coerce'),
            'Costo': pd.to_numeric(df_raw.iloc[:, 6], errors='coerce'),
            'Categoría': 'General'
        }).dropna(subset=['Fecha', 'Costo'])

    # Ordenamos cronológicamente y creamos el periodo
    if not df.empty:
        df = df.sort_values('Fecha')
        df['Mes_Año'] = df['Fecha'].dt.strftime('%Y-%m')
        
    return df

def get_summaries(df):
    """Genera los resúmenes para los gráficos y tablas."""
    ranking = df.groupby('Banco')['Costo'].sum().reset_index().sort_values('Costo', ascending=False)
    mensual = df.groupby(['Mes_Año', 'Banco'])['Costo'].sum().reset_index()
    return ranking, mensual
