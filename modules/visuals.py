import plotly.express as px

def render_charts(df_filt, df_ranking, df_mensual):
    """Genera las figuras para la aplicación respetando el neteo financiero."""
    
    # 1. Barras (Neteado)
    fig_bar = px.bar(
        df_ranking, x='Banco', y='Costo', color='Banco',
        text_auto='.2s', title="Costo Neto Acumulado por Entidad"
    )

    # 2. Pie (Neteado)
    fig_pie = px.pie(df_ranking, values='Costo', names='Banco', hole=0.4)

    # --- 3. DISPERSIÓN CON CLASIFICACIÓN DE CORRECCIONES ---
    df_scatter = df_filt.copy()
    # Usamos el valor absoluto SOLO para el radio del círculo visual
    df_scatter['Tamaño_Visual'] = df_scatter['Costo'].abs()
    # Clasificamos para que el analista vea qué es cargo y qué es corrección
    df_scatter['Tipo_Movimiento'] = df_scatter['Costo'].apply(lambda x: 'Corrección / Neteo' if x < 0 else 'Cargo Normal')

    fig_scatter = px.scatter(
        df_scatter, x='Fecha', y='Costo', color='Banco',
        size='Tamaño_Visual', 
        symbol='Tipo_Movimiento',  # Asigna un símbolo distinto a los negativos
        hover_data=['Banco', 'Costo'], 
        title="Dispersión de Transacciones (Positivos vs. Correcciones)"
    )
    
    # Añadimos una línea punteada en el Cero para separar visualmente los cargos de los neteos
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray")

    # 4. Líneas (Comportamiento Mensual Neteado)
    fig_line = px.line(
        df_mensual, x='Mes_Año', y='Costo', color='Banco', 
        markers=True, title="Tendencia Temporal (Neto Mensual)"
    )

    return fig_bar, fig_pie, fig_scatter, fig_line
