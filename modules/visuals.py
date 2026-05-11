import plotly.express as px

def render_charts(df_filt, df_ranking, df_mensual):
    """Genera los diccionarios de figuras para la app."""
    
    fig_bar = px.bar(
        df_ranking, x='Banco', y='Costo', color='Banco',
        text_auto='.2s', title="Costo Acumulado por Entidad"
    )

    fig_pie = px.pie(df_ranking, values='Costo', names='Banco', hole=0.4)

    fig_scatter = px.scatter(
        df_filt, x='Fecha', y='Costo', color='Banco',
        size='Costo', hover_data=['Banco'], title="Dispersión de Costos"
    )

    fig_line = px.line(
        df_mensual, x='Mes_Año', y='Costo', color='Banco', 
        markers=True, title="Tendencia Temporal"
    )

    return fig_bar, fig_pie, fig_scatter, fig_line
