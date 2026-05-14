import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_charts(df_filt, df_ranking, df_mensual):
    """Genera las figuras para la aplicacion reemplazando dispersion por proyeccion."""
    
    # 1. Barras (Consolidado Neto)
    fig_bar = px.bar(
        df_ranking, x='Banco', y='Costo', color='Banco',
        text_auto='.2s', title="Costo Neto Acumulado por Entidad"
    )

    # 2. Pie (Distribucion)
    fig_pie = px.pie(df_ranking, values='Costo', names='Banco', hole=0.4)

    # --- 3. NUEVO: GRAFICO DE PROYECCION A 3 MESES ---
    # Consolidamos el costo total historico por mes
    df_tot = df_mensual.groupby('Mes_Año')['Costo'].sum().reset_index()
    
    if len(df_tot) > 1:
        # Preparar regresion lineal simple (grado 1)
        x_hist = np.arange(len(df_tot))
        y_hist = df_tot['Costo'].values
        pendiente, intercepto = np.polyfit(x_hist, y_hist, 1)
        
        # Calcular los proximos 3 meses cronologicos
        ultimo_mes_dt = pd.to_datetime(df_tot['Mes_Año'].iloc[-1] + '-01')
        meses_proy = [ultimo_mes_dt + pd.DateOffset(months=i) for i in range(1, 4)]
        str_meses_proy = [m.strftime('%Y-%m') for m in meses_proy]
        
        # Calcular valores proyectados en Y
        x_proy = np.arange(len(df_tot), len(df_tot) + 3)
        y_proy = pendiente * x_proy + intercepto
        
        # Conectar visualmente la linea uniendo el ultimo punto historico con el primer proyectado
        x_linea_proy = [df_tot['Mes_Año'].iloc[-1]] + str_meses_proy
        y_linea_proy = [y_hist[-1]] + list(y_proy)
        
        fig_proy = go.Figure()
        
        # Trazo historico (Linea solida azul)
        fig_proy.add_trace(go.Scatter(
            x=df_tot['Mes_Año'], y=y_hist,
            mode='lines+markers',
            name='Historico Consolidado',
            line=dict(color='#1853A0', width=3),
            marker=dict(size=8)
        ))
        
        # Trazo proyectado (Linea punteada naranja)
        fig_proy.add_trace(go.Scatter(
            x=x_linea_proy, y=y_linea_proy,
            mode='lines+markers',
            name='Proyeccion Estimada (3m)',
            line=dict(color='#FF8C00', width=3, dash='dash'),
            marker=dict(size=8, symbol='star')
        ))
        
        fig_proy.update_layout(
            title="Proyeccion de Costos Totales a 3 Meses (Regresion Lineal)",
            xaxis_title="Periodo Mensual",
            yaxis_title="Monto Neto Estimado",
            template="plotly_white",
            hovermode="x unified"
        )
    else:
        # Fallback elegante si el usuario filtra un rango con un solo mes
        fig_proy = px.bar(
            df_tot, x='Mes_Año', y='Costo',
            title="Proyeccion: Se requieren al menos 2 meses de historial"
        )

    # 4. Lineas (Comportamiento Mensual Individual)
    fig_line = px.line(
        df_mensual, x='Mes_Año', y='Costo', color='Banco', 
        markers=True, title="Evolucion Cronologica por Entidad"
    )

    return fig_bar, fig_pie, fig_proy, fig_line
