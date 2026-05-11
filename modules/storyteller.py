import numpy as np

def generar_narrativa(df_filt, df_ranking, df_mensual):
    """Genera un texto narrativo (storytelling) con análisis de tendencia y proyección."""
    if df_filt.empty or df_ranking.empty or df_mensual.empty:
        return "No hay datos suficientes para generar una narrativa."

    # --- 1. CÁLCULOS BÁSICOS ---
    gasto_total = df_filt['Costo'].sum()
    banco_top = df_ranking.iloc[0]['Banco']
    gasto_top = df_ranking.iloc[0]['Costo']
    pct_top = (gasto_top / gasto_total * 100) if gasto_total > 0 else 0

    correcciones = df_filt[df_filt['Costo'] < 0]
    total_correcciones = correcciones['Costo'].sum()

    mes_top = df_mensual.groupby('Mes_Año')['Costo'].sum().idxmax()
    val_mes_top = df_mensual.groupby('Mes_Año')['Costo'].sum().max()

    # --- 2. NUEVO: PROMEDIO MENSUAL Y TENDENCIA MATEMÁTICA ---
    # Consolidar la serie de tiempo mes a mes totalizada
    serie_mensual = df_mensual.groupby('Mes_Año')['Costo'].sum().reset_index()
    promedio_mensual = serie_mensual['Costo'].mean()

    # Calcular la pendiente (regresión lineal de grado 1) solo si hay más de 1 mes
    if len(serie_mensual) > 1:
        x = np.arange(len(serie_mensual))  # Representa el tiempo como 0, 1, 2...
        y = serie_mensual['Costo'].values  # Los valores de costo neto
        
        # polyfit devuelve [pendiente, intercepto]
        pendiente, _ = np.polyfit(x, y, 1)
        
        # Definimos un pequeño umbral para no llamar "alcista" a variaciones diminutas
        umbral = promedio_mensual * 0.02  # 2% del promedio
        
        if pendiente > umbral:
            tendencia_str = "alcista"
            proyeccion_str = "continúe el incremento en el volumen de costos"
        elif pendiente < -umbral:
            tendencia_str = "bajista"
            proyeccion_str = "continúe el descenso en los costos"
        else:
            tendencia_str = "estable"
            proyeccion_str = "se mantenga un comportamiento lateral, cercano al promedio histórico"
    else:
        tendencia_str = "indeterminada"
        proyeccion_str = "requiere al menos dos periodos mensuales para proyectar una dirección"

    # --- 3. REDACCIÓN DEL STORYTELLING ---
    narrativa = f"### 📌 Resumen Ejecutivo Automático\n\n"
    
    narrativa += f"Durante el periodo analizado, el gasto neto acumulado en las entidades seleccionadas fue de **$ {gasto_total:,.2f}**, con un valor promedio mensual de **$ {promedio_mensual:,.2f}**.\n\n"
    
    narrativa += f"La entidad con mayor volumen neto de costos fue **{banco_top}**, acumulando **$ {gasto_top:,.2f}** (**{pct_top:.1f}%** del total).\n\n"

    if not correcciones.empty:
        narrativa += f"**Impacto de Neteos y Reversiones:** Se detectaron **{len(correcciones)} movimientos de corrección**, representando un ajuste a favor de **$ {abs(total_correcciones):,.2f}** sobre el consolidado.\n\n"
    else:
        narrativa += "**Impacto de Neteos:** No se detectaron reversiones o ajustes negativos.\n\n"

    narrativa += f"**Comportamiento Temporal:** El mes con mayor concentración de costos fue **{mes_top}**, alcanzando un pico de **$ {val_mes_top:,.2f}**.\n\n"

    # Inyección de la conclusión predictiva
    narrativa += f"**Análisis de Tendencia y Proyección:** Al evaluar la serie histórica mes a mes, la tendencia general es **{tendencia_str}**. Basado en este comportamiento, se espera que para el siguiente mes **{proyeccion_str}**."

    return narrativa
