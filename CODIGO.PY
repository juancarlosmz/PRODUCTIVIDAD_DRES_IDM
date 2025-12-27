import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. CONFIGURACIÓN DE URLs ---
file_id_1 = '1sxymGTqTCsHaI-XQkFWu8-r9WEuRPhc_J-KSdQrI9Ho' # Pacientes
file_id_2 = '1vQc4s4zd2bZwT_zB4DGPWk8-ks5obuwc_tSqdAOy4_c' # Tiempos
file_id_3 = '1OXzM_IV5DvCX-OQvdd6UI6s_-K8clz4jyECDLG5G91A' # Envío
file_id_4 = '1bd48YX_rcTaZO3Uxto-m9oq6-va0yOVfBRFqncOG_Do' # Tomas (Usuarios)

urls = [f'https://docs.google.com/spreadsheets/d/{uid}/export?format=xlsx' for uid in [file_id_1, file_id_2, file_id_3, file_id_4]]

try:
    # Carga de datos
    df1 = pd.read_excel(urls[0]); df2 = pd.read_excel(urls[1])
    df3 = pd.read_excel(urls[2]); df4 = pd.read_excel(urls[3])
    
    sedes = ["MIRAFLORES", "JESUS MARÍA", "SURCO"]
    # Nota: Aquí puedes agregar o modificar los nombres de los usuarios según aparezcan en tu Excel
    usuarios_tomas = df4.iloc[:, 0].dropna().unique().tolist() 
    
    meses_nombres = ["MAYO", "JUNIO", "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    
    # Limpieza de nombres de sedes y usuarios (evita errores de espacios o minúsculas)
    for df in [df1, df2, df3, df4]:
        df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip().str.upper()

    df1_sedes = df1[df1.iloc[:, 0].isin(sedes)].copy()
    df1_total = df1[df1.iloc[:, 0] == "TOTAL"].copy()
    df2_sedes = df2[df2.iloc[:, 0].isin(sedes)].copy()
    df3_sedes = df3[df3.iloc[:, 0].isin(sedes)].copy()
    df4_data = df4[df4.iloc[:, 0].isin([u.upper() for u in usuarios_tomas])].copy()

    # --- 2. CREACIÓN DEL DASHBOARD (9 FILAS) ---
    fig = make_subplots(
        rows=9, cols=1, vertical_spacing=0.02,
        subplot_titles=(
            "Semaforo: Cantidad de Pacientes", "Evolución Histórica de Pacientes", "Participación por Sede (%)",
            "Tiempos de Atención (Minutos)", "Tendencia Histórica de Tiempos",
            "Semaforo: Tiempo de Envío", "Tendencia Histórica de Envío",
            "Semaforo: Cantidad de Tomas por Usuario", "Tendencia Histórica de Tomas"
        ),
        specs=[[{"type": "bar"}], [{"type": "scatter"}], [{"type": "pie"}], 
               [{"type": "bar"}], [{"type": "scatter"}], [{"type": "bar"}], 
               [{"type": "scatter"}], [{"type": "bar"}], [{"type": "scatter"}]]
    )

    # --- 3. GENERAR TRACES ---

    # A, B, C: PACIENTES
    for i, mes in enumerate(meses_nombres):
        val = pd.to_numeric(df1_sedes[mes], errors='coerce').fillna(0)
        col = ['#27AE60' if i>0 and a >= pd.to_numeric(df1_sedes[meses_nombres[i-1]], errors='coerce').fillna(0).iloc[idx] else '#E74C3C' for idx, a in enumerate(val)] if i>0 else '#3498DB'
        fig.add_trace(go.Bar(x=df1_sedes.iloc[:, 0], y=val, marker_color=col, visible=(mes=="DICIEMBRE"), text=val, textposition='outside', showlegend=False), row=1, col=1)
    for s in sedes:
        fig.add_trace(go.Scatter(x=meses_nombres, y=[df1_sedes[df1_sedes.iloc[:, 0]==s][m].values[0] if not df1_sedes[df1_sedes.iloc[:, 0]==s].empty else 0 for m in meses_nombres], name=f"Pac. {s}"), row=2, col=1)
    for mes in meses_nombres:
        fig.add_trace(go.Pie(labels=df1_sedes.iloc[:, 0], values=pd.to_numeric(df1_sedes[mes], errors='coerce').fillna(0), visible=(mes=="DICIEMBRE")), row=3, col=1)

    # D, E: TIEMPOS ATENCIÓN
    for i, mes in enumerate(meses_nombres):
        val = pd.to_numeric(df2_sedes[mes], errors='coerce').fillna(0)
        col = ['#27AE60' if i>0 and a <= pd.to_numeric(df2_sedes[meses_nombres[i-1]], errors='coerce').fillna(0).iloc[idx] else '#E74C3C' for idx, a in enumerate(val)] if i>0 else '#9B59B6'
        fig.add_trace(go.Bar(x=df2_sedes.iloc[:, 0], y=val, marker_color=col, visible=(mes=="DICIEMBRE"), text=val, textposition='outside', showlegend=False), row=4, col=1)
    for s in sedes:
        fig.add_trace(go.Scatter(x=meses_nombres, y=[df2_sedes[df2_sedes.iloc[:, 0]==s][m].values[0] if not df2_sedes[df2_sedes.iloc[:, 0]==s].empty else 0 for m in meses_nombres], name=f"Reloj {s}"), row=5, col=1)

    # F, G: TIEMPOS ENVÍO
    for i, mes in enumerate(meses_nombres):
        val = pd.to_numeric(df3_sedes[mes], errors='coerce').fillna(0)
        col = ['#27AE60' if i>0 and a <= pd.to_numeric(df3_sedes[meses_nombres[i-1]], errors='coerce').fillna(0).iloc[idx] else '#E74C3C' for idx, a in enumerate(val)] if i>0 else '#F1C40F'
        fig.add_trace(go.Bar(x=df3_sedes.iloc[:, 0], y=val, marker_color=col, visible=(mes=="DICIEMBRE"), text=val, textposition='outside', showlegend=False), row=6, col=1)
    for s in sedes:
        fig.add_trace(go.Scatter(x=meses_nombres, y=[df3_sedes[df3_sedes.iloc[:, 0]==s][m].values[0] if not df3_sedes[df3_sedes.iloc[:, 0]==s].empty else 0 for m in meses_nombres], name=f"Envío {s}"), row=7, col=1)

    # H, I: TOMAS POR USUARIO (Usando df4)
    for i, mes in enumerate(meses_nombres):
        val = pd.to_numeric(df4_data[mes], errors='coerce').fillna(0)
        col = ['#27AE60' if i>0 and a >= pd.to_numeric(df4_data[meses_nombres[i-1]], errors='coerce').fillna(0).iloc[idx] else '#E74C3C' for idx, a in enumerate(val)] if i>0 else '#1ABC9C'
        fig.add_trace(go.Bar(x=df4_data.iloc[:, 0], y=val, marker_color=col, visible=(mes=="DICIEMBRE"), text=val, textposition='outside', showlegend=False), row=8, col=1)
    for u in usuarios_tomas:
        u_up = u.upper()
        fig.add_trace(go.Scatter(x=meses_nombres, y=[df4_data[df4_data.iloc[:, 0]==u_up][m].values[0] if not df4_data[df4_data.iloc[:, 0]==u_up].empty else 0 for m in meses_nombres], name=f"Tomas: {u}"), row=9, col=1)

    # --- 4. BOTONES DE FILTRADO ---
    botones = []
    for i, mes in enumerate(meses_nombres):
        # Visibilidad: Barras del mes (P, T, E, To) + Líneas históricas (siempre True)
        # Calculamos la visibilidad trace por trace
        mask = []
        # Agrupamos la lógica de visibilidad para los 9 gráficos
        for trace in fig.data:
            if isinstance(trace, go.Bar) or isinstance(trace, go.Pie):
                mask.append(mes in (trace.name if trace.name else "") or trace.visible == (mes == "DICIEMBRE"))
            else:
                mask.append(True) # Scatters siempre visibles

        # Corrección manual de máscara para asegurar sincronía perfecta
        m_final = [False]*len(fig.data)
        # Índices manuales basados en la construcción:
        m_final[i] = True # Bar Pac
        m_final[8:12] = [True]*4 # Line Pac
        m_final[12+i] = True # Pie
        m_final[20+i] = True # Bar Time
        m_final[28:31] = [True]*3 # Line Time
        m_final[31+i] = True # Bar Env
        m_final[39:42] = [True]*3 # Line Env
        m_final[42+i] = True # Bar Tomas
        m_final[50:] = [True]*len(usuarios_tomas) # Line Tomas

        botones.append(dict(label=f"MES: {mes}", method="update", args=[{"visible": m_final}]))

    fig.update_layout(
        updatemenus=[dict(active=7, buttons=botones, x=0.01, y=1.03)],
        title='<b>CONTROL GERENCIAL INTEGRADO</b>',
        height=3800, template='plotly_white', margin=dict(t=150, b=50)
    )
    #fig.show()

    fig.write_html("index.html", full_html=True, include_plotlyjs='cdn')
    print("¡Archivo index.html generado con éxito!")

except Exception as e:
    print(f"Error en la integración: {e}")
