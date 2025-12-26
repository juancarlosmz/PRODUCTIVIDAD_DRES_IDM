import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Configuración de la URL y Carga de Datos
file_id = '1sxymGTqTCsHaI-XQkFWu8-r9WEuRPhc_J-KSdQrI9Ho'
url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'

try:
    df = pd.read_excel(url)
    
    # Definición de estructuras
    sedes = ["MIRAFLORES", "JESUS MARÍA", "SURCO"]
    meses_nombres = ["MAYO", "JUNIO", "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    
    df_sedes = df[df.iloc[:, 0].isin(sedes)].copy()
    df_total = df[df.iloc[:, 0] == "TOTAL"].copy()

    # --- CREACIÓN DEL DASHBOARD ---
    fig = make_subplots(
        rows=3, cols=1,
        vertical_spacing=0.08,
        subplot_titles=("Semaforo Comparativo Mensual", "Evolución Histórica (Tendencia)", "Participación por Sede"),
        specs=[[{"type": "bar"}], [{"type": "scatter"}], [{"type": "pie"}]]
    )

    # 2. GENERAR TRACES DE BARRAS (Uno por mes)
    for i, mes in enumerate(meses_nombres):
        valores_actuales = pd.to_numeric(df_sedes[mes], errors='coerce').fillna(0)
        if i > 0:
            mes_previo = meses_nombres[i-1]
            valores_previos = pd.to_numeric(df_sedes[mes_previo], errors='coerce').fillna(0)
            colores = ['#27AE60' if a >= p else '#E74C3C' for a, p in zip(valores_actuales, valores_previos)]
        else:
            colores = '#3498DB'

        fig.add_trace(go.Bar(
            x=df_sedes.iloc[:, 0], y=valores_actuales,
            name=f"Bar {mes}", text=valores_actuales, textposition='outside',
            marker_color=colores, visible=(mes == "DICIEMBRE"), showlegend=False
        ), row=1, col=1)

    # 3. GENERAR TRACES DE LÍNEAS (Estáticos - Muestran todo el año)
    for sede in sedes:
        fila_sede = df_sedes[df_sedes.iloc[:, 0] == sede]
        valores_hist = [fila_sede[m].values[0] for m in meses_nombres]
        fig.add_trace(go.Scatter(
            x=meses_nombres, y=valores_hist, mode='lines+markers',
            name=sede, line=dict(width=3), visible=True
        ), row=2, col=1)

    # Línea de Total
    valores_total = [df_total[m].values[0] for m in meses_nombres]
    fig.add_trace(go.Scatter(
        x=meses_nombres, y=valores_total, mode='lines+markers+text',
        name="TOTAL", text=valores_total, textposition="top center",
        line=dict(color='black', dash='dash'), visible=True
    ), row=2, col=1)

    # 4. GENERAR TRACES DE PIE (Uno por mes para que el filtro funcione)
    for mes in meses_nombres:
        valores_pie = pd.to_numeric(df_sedes[mes], errors='coerce').fillna(0)
        fig.add_trace(go.Pie(
            labels=df_sedes.iloc[:, 0], values=valores_pie,
            name=f"Pie {mes}", hole=.4,
            marker=dict(colors=['#3498DB', '#9B59B6', '#F1C40F']),
            visible=(mes == "DICIEMBRE"),
            textinfo='label+percent'
        ), row=3, col=1)

    # --- 5. LÓGICA DE FILTRADO SINCRONIZADO ---
    # Índices:
    # 0 a 7: Barras (8 traces)
    # 8 a 11: Líneas (4 traces - SIEMPRE VISIBLES)
    # 12 a 19: Pies (8 traces)

    botones = []
    num_meses = len(meses_nombres)
    total_lineas = 4

    for i, mes in enumerate(meses_nombres):
        # Crear máscara de visibilidad
        v_barras = [False] * num_meses
        v_lineas = [True] * total_lineas
        v_pies = [False] * num_meses
        
        v_barras[i] = True  # Activa la barra del mes i
        v_pies[i] = True    # Activa el pie del mes i
        
        visibilidad_total = v_barras + v_lineas + v_pies
        
        botones.append(dict(
            label=f"MES: {mes}",
            method="update",
            args=[{"visible": visibilidad_total},
                  {"title": f"<b>ANÁLISIS DE PACIENTES - {mes}</b>"}]
        ))

    # 6. DISEÑO FINAL
    fig.update_layout(
        updatemenus=[dict(
            active=num_meses-1,
            buttons=botones,
            direction="down", x=0.01, y=1.1, showactive=True,
            bgcolor="#F8F9F9", bordercolor="#D5DBDB"
        )],
        title='<b>DASHBOARD INTEGRAL DE PACIENTES</b>',
        title_x=0.5,
        template='plotly_white',
        height=1300,
        margin=dict(t=150, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=0.35, xanchor="center", x=0.5)
    )

    # Ajustes estéticos de ejes
    fig.update_xaxes(title_text="Evolución Mensual", row=2, col=1)
    fig.update_yaxes(title_text="Cantidad de Pacientes", row=1, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray', row=2, col=1)

    fig.show()

except Exception as e:
    print(f"Error al sincronizar el dashboard: {e}")
