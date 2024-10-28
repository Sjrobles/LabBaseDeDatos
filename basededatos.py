import streamlit as st  # type: ignore
import pandas as pd
import pyodbc
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="NBA Shot Statistics", page_icon="🏀", layout="wide")

# Función para conectar a SQL Server
def conexion_sql_server():
    conn = pyodbc.connect(
        Trusted_Connection='yes',
        driver='{ODBC Driver 17 for SQL Server}',
        server='DESKTOP-LDJ6I50\\SQLEXPRESS',
        database='NBA_Shots'
    )    
    return conn

# Función para ejecutar la consulta SQL y devolver un DataFrame (sin cerrar la conexión)
def select_to_df(sql_query, conn):
    try:
        df = pd.read_sql(sql_query, conn)
    except Exception as e:
        st.write(f"Error: {e}")
        df = pd.DataFrame()  # Devuelve un DataFrame vacío si hay error
    return df

# Conexión a la base de datos (mantener la conexión abierta)
conexion = conexion_sql_server()

# Consulta para obtener los equipos
query_teams = "SELECT TEAM_ID, TEAM_NAME FROM dbo.teams"
df_teams = select_to_df(query_teams, conexion)

# Crear diccionario de equipos
teams_dict = dict(zip(df_teams.TEAM_NAME, df_teams.TEAM_ID))

# Asignación de colores personalizados a todos los equipos de la NBA
team_colors = {
    'Atlanta Hawks': '#E03A3E',
    'Boston Celtics': '#007A33',
    'Brooklyn Nets': '#000000',
    'Charlotte Hornets': '#1D1160',
    'Chicago Bulls': '#CE1141',
    'Cleveland Cavaliers': '#860038',
    'Dallas Mavericks': '#00538C',
    'Denver Nuggets': '#0E2240',
    'Detroit Pistons': '#C8102E',
    'Golden State Warriors': '#1D428A',
    'Houston Rockets': '#CE1141',
    'Indiana Pacers': '#002D62',
    'Los Angeles Clippers': '#C8102E',
    'Los Angeles Lakers': '#552583',
    'Memphis Grizzlies': '#5D76A9',
    'Miami Heat': '#98002E',
    'Milwaukee Bucks': '#00471B',
    'Minnesota Timberwolves': '#0C2340',
    'New Orleans Pelicans': '#0C2340',
    'New York Knicks': '#006BB6',
    'Oklahoma City Thunder': '#007AC1',
    'Orlando Magic': '#0077C0',
    'Philadelphia 76ers': '#006BB6',
    'Phoenix Suns': '#1D1160',
    'Portland Trail Blazers': '#E03A3E',
    'Sacramento Kings': '#5A2D81',
    'San Antonio Spurs': '#C4CED4',
    'Toronto Raptors': '#CE1141',
    'Utah Jazz': '#002B5C',
    'Washington Wizards': '#002B5C'
}

# Sidebar para selección de equipos y jugadores
with st.sidebar:
    selected_team = st.selectbox("Selecciona un equipo", options=list(teams_dict.keys()))
    team_id = teams_dict[selected_team]

    # Consulta para obtener los jugadores del equipo seleccionado
    query_players = f"""
    SELECT DISTINCT p.PLAYER_ID, p.PLAYER_NAME 
    FROM dbo.players p
    JOIN dbo.shots s ON p.PLAYER_ID = s.PLAYER_ID
    WHERE s.TEAM_ID = '{team_id}'
    """
    df_players = select_to_df(query_players, conexion)
    player_dict = dict(zip(df_players.PLAYER_NAME, df_players.PLAYER_ID))
    selected_player = st.selectbox("Selecciona un jugador:", options=list(player_dict.keys()))

# Consulta y gráfica de puntos de 2PT y 3PT
query_shots = f"""
SELECT SHOT_TYPE, COUNT(*) as Shot_Count
FROM dbo.shots
WHERE TEAM_ID = '{team_id}' AND SHOT_MADE = 1
GROUP BY SHOT_TYPE
"""
df_shots = select_to_df(query_shots, conexion)

# Mostrar gráfica de puntos de 2PT y 3PT
st.title("Análisis de Tiros de la NBA")
st.subheader(f"Tiros de 2PT y 3PT para el equipo {selected_team}")
fig = px.bar(df_shots, x='SHOT_TYPE', y='Shot_Count', title='Tiros de 2PT y 3PT',
             color_discrete_sequence=[team_colors.get(selected_team, '#636EFA')])
fig.update_layout(title='Tiros de 2PT y 3PT',
                  xaxis_title='Tipo de Tiro',
                  yaxis_title='Conteo de Tiros',
                  template='plotly_white')
st.plotly_chart(fig)

# Gráfica de estadísticas por jugador (Gráfico circular - Pie Chart)
player_id = player_dict[selected_player]
st.subheader(f"Tiros realizados por {selected_player}")
query_player_stats = f"""
SELECT 
    SHOT_TYPE, 
    COUNT(*) as Shot_Count
FROM 
    dbo.shots
WHERE 
    PLAYER_ID = '{player_id}' AND
    SHOT_MADE = 1
GROUP BY 
    SHOT_TYPE
"""
df_player_stats = select_to_df(query_player_stats, conexion)

# Gráfico circular (Pie chart) 
colors = ['#FF9999', '#66B3FF']  # Colores para 2PT y 3PT
fig_player_stats = px.pie(df_player_stats, values='Shot_Count', names='SHOT_TYPE', 
                          title=f'Distribución de tiros de 2PT y 3PT de {selected_player}',
                          color_discrete_sequence=colors)
fig_player_stats.update_layout(
    title=f'Distribución de tiros de 2PT y 3PT de {selected_player}',
    template='plotly_white'
)
st.plotly_chart(fig_player_stats)

# Heatmap de zonas de tiro
st.subheader(f"Mapa de calor de las zonas de tiro para el equipo {selected_team}")
query_heatmap = f"""
SELECT LOC_X, LOC_Y, COUNT(*) as Shot_Count
FROM dbo.shots
WHERE TEAM_ID = '{team_id}' AND SHOT_MADE = 1
GROUP BY LOC_X, LOC_Y
"""
df_heatmap = select_to_df(query_heatmap, conexion)

# Heatmap
fig_heatmap = px.density_heatmap(df_heatmap, x='LOC_X', y='LOC_Y', z='Shot_Count', 
                                  title='Mapa de calor de zonas de tiro')

# Agregar imagen de fondo de la cancha
fig_heatmap.update_layout(
    title='Mapa de calor de zonas de tiro',
    xaxis_title='Localización X',
    yaxis_title='Localización Y',
    template='plotly_white',
    images=[dict(
        source="URL_DE_LA_IMAGEN_DE_LA_CANCHA",  # Reemplaza con la URL real
        x=0,
        y=0,
        xref="x",
        yref="y",
        sizex=100,  # Ajusta el tamaño según sea necesario
        sizey=50,
        xanchor="center",
        yanchor="middle",
        opacity=0.5,  # Ajusta la opacidad si es necesario
        layer="below"
    )]
)
st.plotly_chart(fig_heatmap)

# Comparación entre equipos
st.write("### Comparación de equipos")
team1 = st.selectbox("Equipo 1", options=list(teams_dict.keys()), key="team1")
team2 = st.selectbox("Equipo 2", options=list(teams_dict.keys()), key="team2")

team1_id = teams_dict[team1]
team2_id = teams_dict[team2]

# Consulta para obtener estadísticas de los dos equipos
query_compare = f"""
SELECT TEAM_ID, SHOT_TYPE, COUNT(*) as Shot_Count
FROM dbo.shots
WHERE TEAM_ID IN ('{team1_id}', '{team2_id}') AND SHOT_MADE = 1
GROUP BY TEAM_ID, SHOT_TYPE
"""
df_compare = select_to_df(query_compare, conexion)

# Gráfica de comparación entre equipos con gráfico de burbujas
st.subheader(f"Comparación de tiros entre {team1} y {team2} (Equipo 1 Azul Oscuro , Equipo 2 Azul Claro)")

if not df_compare.empty:
    fig_bubble_compare = px.scatter(df_compare,
                                     x='SHOT_TYPE',
                                     y='Shot_Count',
                                     color='TEAM_ID',
                                     size='Shot_Count',  # El tamaño de la burbuja se basa en el conteo de tiros
                                     hover_name='TEAM_ID',  # Mostrar el nombre del equipo al pasar el ratón
                                     size_max=30,  # Tamaño máximo de las burbujas
                                     title='Comparación de tiros entre dos equipos',
                                     color_discrete_map={
                                         team1_id: team_colors.get(team1, '#636EFA'), 
                                         team2_id: team_colors.get(team2, '#EF553B')
                                     })
    
    # Ajustar el layout
    fig_bubble_compare.update_layout(
        title='Comparación de tiros entre equipos',
        xaxis_title='Tipo de Tiro',
        yaxis_title='Conteo de Tiros',
        template='plotly_white'
    )
    
    # Mostrar la gráfica
    st.plotly_chart(fig_bubble_compare)
else:
    st.write("No hay datos disponibles para la comparación entre estos equipos.")


# Gráfica de dispersión por zona de tiro y si fue acertado o no
st.subheader(f"Distribución de tiros por zona y acierto para el equipo {selected_team}")
query_zone_shots = f"""
SELECT ZONE_NAME, SHOT_MADE, COUNT(*) as Shot_Count
FROM dbo.shots
WHERE TEAM_ID = '{team_id}'
GROUP BY ZONE_NAME, SHOT_MADE
"""
df_zone_shots = select_to_df(query_zone_shots, conexion)

# Gráfico de dispersión (Scatter plot)
fig_zone_shots = px.scatter(df_zone_shots, x='ZONE_NAME', y='Shot_Count', color='SHOT_MADE',
                             title=f'Distribución de tiros por zona de {selected_team}',
                             color_discrete_map={1: 'green', 0: 'red'})
fig_zone_shots.update_layout(title='Distribución de tiros por zona de tiro',
                              xaxis_title='Zona de Tiro',
                              yaxis_title='Conteo de Tiros',
                              template='plotly_white')
st.plotly_chart(fig_zone_shots)

# Selección de estadio y visualización en mapa
st.subheader("Selecciona un estadio para visualizar en el mapa")

# Obtener la lista de estadios
query_stadiums = "SELECT STADIUM_NAME, N_STADIUM, W_STADIUM FROM dbo.stadium"
stadium_info = select_to_df(query_stadiums, conexion)

# Crear un menú desplegable para los estadios
stadium_names = stadium_info['STADIUM_NAME'].tolist()
selected_stadium = st.selectbox("Selecciona un estadio", options=stadium_names)

# Obtener la información del estadio seleccionado
stadium_data = stadium_info[stadium_info['STADIUM_NAME'] == selected_stadium]
if not stadium_data.empty:
    n_estadium = stadium_data['N_STADIUM'].iloc[0]
    w_estadium = stadium_data['W_STADIUM'].iloc[0]

    st.write(f"Estadio: {selected_stadium}")

    # Mostrar ubicación del estadio en el mapa
    st.map(pd.DataFrame({
        'lat': [n_estadium],
        'lon': [w_estadium]
    }))
else:
    st.write("No se encontró información sobre el estadio.")


# Gráfica de distancia de tiro a través del tiempo
query_shot_distance = f"""
SELECT 
    DATEPART(YEAR, g.GAME_DATE) AS Year, 
    DATEPART(QUARTER, g.GAME_DATE) AS Quarter,
    AVG(s.SHOT_DISTANCE) AS Average_Shot_Distance
FROM 
    dbo.shots s
JOIN 
    dbo.Games g ON s.GAME_ID = g.GAME_ID
WHERE 
    s.TEAM_ID = '{team_id}' AND 
    g.GAME_DATE >= '2022-10-01' AND 
    g.GAME_DATE <= '2023-08-31' 
GROUP BY 
    DATEPART(YEAR, g.GAME_DATE), 
    DATEPART(QUARTER, g.GAME_DATE)
ORDER BY 
    Year, Quarter
"""
df_shot_distance = select_to_df(query_shot_distance, conexion)


# Crear una nueva columna para el trimestre
df_shot_distance['Year_Quarter'] = df_shot_distance['Year'].astype(str) + '-Q' + df_shot_distance['Quarter'].astype(str)

# Gráfica de la distancia de tiro por trimestre
st.subheader(f"Cambio en la distancia de tiro del equipo {selected_team} cada 3 meses")
if not df_shot_distance.empty:  # Verificar que no esté vacío
    fig_distance = px.line(df_shot_distance, x='Year_Quarter', y='Average_Shot_Distance',
                           title=f"Cambio en la distancia de tiro del equipo {selected_team} cada 3 meses",
                           markers=True)
    fig_distance.update_layout(
        title='Cambio en la distancia de tiro cada 3 meses',
        xaxis_title='Año-Trimestre',
        yaxis_title='Distancia Promedio de Tiro (pies)',
        template='plotly_white'
    )
    st.plotly_chart(fig_distance)
else:
    st.write("No hay datos disponibles para mostrar.")




# Cierre de la conexión (opcional, según tu lógica)
conexion.close()