import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. CONFIGURACIÓN DE URLs Y CARGA DE DATOS ---
file_id_1 = '1sxymGTqTCsHaI-XQkFWu8-r9WEuRPhc_J-KSdQrI9Ho' # Pacientes
url_1 = f'https://docs.google.com/spreadsheets/d/{file_id_1}/export?format=xlsx'

file_id_2 = '1vQc4s4zd2bZwT_zB4DGPWk8-ks5obuwc_tSqdAOy4_c' # Tiempos
url_2 = f'https://docs.google.com/spreadsheets/d/{file_id_2}/export?format=xlsx'

try:
    df1 = pd.read_excel(url_1)
    df2 = pd.read_excel(url_2)
    
    sedes = ["MIRAFLORES", "JESUS MARÍA", "SURCO"]
    meses_nombres = ["MAYO", "JUNIO", "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    
    df1_sedes = df1[df1.iloc[:, 0].isin(sedes)].copy()
    df1_total = df1[df1.iloc[:, 0] == "TOTAL"].copy()
    df2_sedes = df2[df2.iloc[:, 0].isin(sedes)].copy()

    # --- 2. CREACIÓN DEL DASHBOARD (5 FILAS) ---
    fig = make_subplots(
        rows=5, cols=1,
        vertical_spacing=0.05,
        subplot_titles=(
            "Semaforo: Cantidad de Pacientes", 
            "Evolución Histórica de Pacientes", 
            "Participación por Sede (%)",
            "<b>Tiempos de Atención por Mes (Minutos)</b>",
            "Tendencia Histórica de Tiempos (Rapidez)"
        ),
        specs=[[{"type": "bar"}], [{"type": "scatter"}], [{"type": "pie"}], [{"type": "bar"}], [{"type": "scatter"}]]
    )

    # --- 3. GENERAR TRACES ---

    # A. BARRAS PACIENTES (Fila 1) - 8 traces (0-7)
    for i, mes in enumerate(meses_nombres):
        valores = pd.to_numeric(df1_sedes[mes], errors='coerce').fillna(0)
        colores = '#3498DB'
        if i > 0:
            prev = pd.to_numeric(df1_sedes[meses_nombres[i-1]], errors='coerce').fillna(0)
            colores = ['#27AE60' if a >= p else '#E74C3C' for a, p in zip(valores, prev)]
        
        fig.add_trace(go.Bar(
            x=df1_sedes.iloc[:, 0], y=valores, name=f"Pac. {mes}",
            text=valores, textposition='outside', marker_color=colores,
            visible=(mes == "DICIEMBRE"), showlegend=False
        ), row=1, col=1)

    # B. TENDENCIA PACIENTES (Fila 2 - Estática) - 4 traces (8-11)
    for sede in sedes:
        val_h = [df1_sedes[df1_sedes.iloc[:, 0] == sede][m].values[0] for m in meses_nombres]
        fig.add_trace(go.Scatter(x=meses_nombres, y=val_h, name=f"Pac. {sede}", mode='lines+markers'), row=2, col=1)
    
    val_t = [df1_total[m].values[0] for m in meses_nombres]
    fig.add_trace(go.Scatter(x=meses_nombres, y=val_t, name="TOTAL PAC.", line=dict(dash='dash', color='black')), row=2, col=1)

    # C. PIE PARTICIPACIÓN (Fila 3) - 8 traces (12-19)
    for mes in meses_nombres:
        val_p = pd.to_numeric(df1_sedes[mes], errors='coerce').fillna(0)
        fig.add_trace(go.Pie(
            labels=df1_sedes.iloc[:, 0], values=val_p, hole=.4,
            visible=(mes == "DICIEMBRE"), textinfo='label+percent'
        ), row=3, col=1)

    # D. BARRAS TIEMPOS (Fila 4) - 8 traces (20-27)
    for i, mes in enumerate(meses_nombres):
        val_tiempos = pd.to_numeric(df2_sedes[mes], errors='coerce').fillna(0)
        # Semáforo inverso para tiempos: si BAJA el tiempo es VERDE
        colores_t = '#9B59B6'
        if i > 0:
            prev_t = pd.to_numeric(df2_sedes[meses_nombres[i-1]], errors='coerce').fillna(0)
            colores_t = ['#27AE60' if a <= p else '#E74C3C' for a, p in zip(val_tiempos, prev_t)]

        fig.add_trace(go.Bar(
            x=df2_sedes.iloc[:, 0], y=val_tiempos, name=f"T. {mes}",
            text=val_tiempos, textposition='outside', marker_color=colores_t,
            visible=(mes == "DICIEMBRE"), showlegend=False
        ), row=4, col=1)

    # E. TENDENCIA TIEMPOS (Fila 5 - Estática) - 3 traces (28-30)
    for sede in sedes:
        val_th = [df2_sedes[df2_sedes.iloc[:, 0] == sede][m].values[0] for m in meses_nombres]
        fig.add_trace(go.Scatter(
            x=meses_nombres, y=val_th, name=f"Reloj {sede}", 
            mode='lines+markers', line=dict(shape='spline')
        ), row=5, col=1)

    # --- 4. LÓGICA DE FILTRADO ---
    botones = []
    num_meses = 8
    for i, mes in enumerate(meses_nombres):
        v_pac_bar = [False] * 8
        v_pac_line = [True] * 4
        v_pie = [False] * 8
        v_time_bar = [False] * 8
        v_time_line = [True] * 3
        
        v_pac_bar[i] = True
        v_pie[i] = True
        v_time_bar[i] = True
        
        visibilidad_total = v_pac_bar + v_pac_line + v_pie + v_time_bar + v_time_line
        
        botones.append(dict(
            label=f"MES: {mes}",
            method="update",
            args=[{"visible": visibilidad_total},
                  {"title": f"<b>DASHBOARD GERENCIAL - CONTROL {mes}</b>"}]
        ))

    # --- 5. DISEÑO FINAL ---
    fig.update_layout(
        updatemenus=[dict(
            active=num_meses-1,
            buttons=botones,
            direction="down", x=0.01, y=1.06, showactive=True
        )],
        title='<b>DASHBOARD INTEGRAL DE RENDIMIENTO</b>',
        title_x=0.5,
        template='plotly_white',
        height=2000, # Aumentado para 5 gráficas
        margin=dict(t=150, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=0.42, xanchor="center", x=0.5)
    )

    fig.update_yaxes(title_text="Pacientes", row=1, col=1)
    fig.update_yaxes(title_text="Minutos", row=4, col=1)
    fig.update_yaxes(title_text="Minutos", row=5, col=1)

    # fig.show()
    
    fig.write_html("index.html", full_html=True, include_plotlyjs='cdn')
    print("¡Archivo index.html generado con éxito!")

except Exception as e:
    print(f"Error en la integración: {e}")
