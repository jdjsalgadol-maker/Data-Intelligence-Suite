import pandas as pd

def clean_and_prepare_data(archivo):
    """Carga y prepara las columnas B, D y G."""
    df_raw = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
    
    # Mapeo de columnas (B=1, D=3, G=6)
    df = pd.DataFrame({
        'Banco': df_raw.iloc[:, 1],
        'Fecha': pd.to_datetime(df_raw.iloc[:, 3], dayfirst=True, errors='coerce'),
        'Costo': pd.to_numeric(df_raw.iloc[:, 6], errors='coerce')
    }).dropna(subset=['Fecha', 'Costo'])

    df = df.sort_values('Fecha')
    df['Mes_Año'] = df['Fecha'].dt.strftime('%Y-%m')
    return df

def get_summaries(df):
    """Genera los resúmenes para los gráficos."""
    ranking = df.groupby('Banco')['Costo'].sum().reset_index().sort_values('Costo', ascending=False)
    mensual = df.groupby(['Mes_Año', 'Banco'])['Costo'].sum().reset_index()
    return ranking, mensual
