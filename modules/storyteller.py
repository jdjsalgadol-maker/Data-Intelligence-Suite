def generar_narrativa(df_filt, df_ranking, df_mensual):
    """Genera un texto narrativo (storytelling) basado en las cifras financieras."""
    if df_filt.empty or df_ranking.empty:
        return "No hay datos suficientes para generar una narrativa."

    gasto_total = df_filt['Costo'].sum()
    banco_top = df_ranking.iloc[0]['Banco']
    gasto_top = df_ranking.iloc[0]['Costo']
    
    # Cálculo de participación
    pct_top = (gasto_top / gasto_total * 100) if gasto_total > 0 else 0

    # Análisis de neteos/correcciones (valores negativos)
    correcciones = df_filt[df_filt['Costo'] < 0]
    total_correcciones = correcciones['Costo'].sum()

    # Análisis temporal
    mes_top = df_mensual.groupby('Mes_Año')['Costo'].sum().idxmax()
    val_mes_top = df_mensual.groupby('Mes_Año')['Costo'].sum().max()

    # Redacción dinámica
    narrativa = f"### 📌 Resumen Ejecutivo Automático\n\n"
    narrativa += f"Durante el periodo analizado, el gasto neto acumulado en todas las entidades seleccionadas fue de **$ {gasto_total:,.2f}**. "
    narrativa += f"La entidad que representó el mayor volumen neto de costos fue **{banco_top}**, acumulando **$ {gasto_top:,.2f}**, lo que equivale al **{pct_top:.1f}%** del gasto total.\n\n"

    if not correcciones.empty:
        narrativa += f"**Impacto de Neteos y Reversiones:** El sistema detectó **{len(correcciones)} movimientos de corrección** (valores negativos), los cuales representaron un ajuste neto a favor de **$ {total_correcciones:,.2f}** sobre el consolidado final.\n\n"
    else:
        narrativa += "**Impacto de Neteos:** No se detectaron reversiones o ajustes negativos durante estos periodos.\n\n"

    narrativa += f"**Comportamiento Temporal:** El mes con la mayor concentración de costos netos fue **{mes_top}**, alcanzando un pico de **$ {val_mes_top:,.2f}**."

    return narrativa
