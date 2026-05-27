import streamlit as st
import fastf1
import pandas as pd
import plotly.express as px

# ---------------------------------
# CONFIG PAGE
# ---------------------------------
st.set_page_config(
    page_title="AI Motorsport Performance Assistant",
    layout="wide"
)

# ---------------------------------
# TITRE
# ---------------------------------
st.title("🏎️ AI Motorsport Performance Assistant")
st.markdown("### Analyse de performance F1 • Motorsport Analytics")

# ---------------------------------
# SIDEBAR
# ---------------------------------
st.sidebar.header("⚙️ Paramètres")

year = st.sidebar.selectbox(
    "Saison",
    [2024, 2023, 2022]
)

grand_prix = st.sidebar.selectbox(
    "Grand Prix",
    ["Monaco", "Silverstone", "Monza", "Spa"]
)

session_type = st.sidebar.selectbox(
    "Session",
    ["R", "Q", "FP1"]
)

# ---------------------------------
# CHARGEMENT SESSION
# ---------------------------------
st.subheader("📊 Chargement des données F1")

with st.spinner("Chargement des données..."):

    session = fastf1.get_session(
        year,
        grand_prix,
        session_type
    )

    session.load()

st.success("Données chargées avec succès ✅")

# ---------------------------------
# RESULTATS
# ---------------------------------
results = session.results

df = results[[
    "Abbreviation",
    "TeamName",
    "Position",
    "Points"
]]

df.columns = [
    "Pilote",
    "Équipe",
    "Position",
    "Points"
]

st.subheader("🏁 Résultats")

st.dataframe(
    df,
    use_container_width=True
)

# ---------------------------------
# COMPARAISON PILOTES
# ---------------------------------
st.subheader("⚔️ Comparaison pilotes")

col1, col2 = st.columns(2)

with col1:
    driver_1 = st.selectbox(
        "Pilote 1",
        df["Pilote"],
        index=0
    )

with col2:
    driver_2 = st.selectbox(
        "Pilote 2",
        df["Pilote"],
        index=1
    )

laps_1 = session.laps.pick_drivers(driver_1)
laps_2 = session.laps.pick_drivers(driver_2)

laps_1 = laps_1.dropna(subset=["LapTime"])
laps_2 = laps_2.dropna(subset=["LapTime"])

laps_1["LapTimeSeconds"] = laps_1[
    "LapTime"
].dt.total_seconds()

laps_2["LapTimeSeconds"] = laps_2[
    "LapTime"
].dt.total_seconds()

laps_1 = laps_1[
    laps_1["LapTimeSeconds"] < 200
]

laps_2 = laps_2[
    laps_2["LapTimeSeconds"] < 200
]

laps_1["Pilote"] = driver_1
laps_2["Pilote"] = driver_2

comparison_df = pd.concat([
    laps_1,
    laps_2
])

# ---------------------------------
# STATS
# ---------------------------------
st.subheader("📊 Statistiques pilotes")

stat1, stat2 = st.columns(2)

with stat1:

    st.metric(
        f"⏱️ Best Lap {driver_1}",
        f"{laps_1['LapTimeSeconds'].min():.2f}s"
    )

with stat2:

    st.metric(
        f"⏱️ Best Lap {driver_2}",
        f"{laps_2['LapTimeSeconds'].min():.2f}s"
    )

# ---------------------------------
# GRAPH TEMPS
# ---------------------------------
st.subheader("📈 Évolution des temps")

fig_compare = px.line(
    comparison_df,
    x="LapNumber",
    y="LapTimeSeconds",
    color="Pilote",
    title=f"{driver_1} vs {driver_2}"
)

st.plotly_chart(
    fig_compare,
    use_container_width=True
)

# ---------------------------------
# TELEMETRIE
# ---------------------------------
st.subheader("📡 Télémétrie")

selected_driver = st.selectbox(
    "Choisir un pilote télémétrie",
    df["Pilote"]
)

driver_laps = session.laps.pick_drivers(
    selected_driver
)

fastest_lap = driver_laps.pick_fastest()

telemetry = fastest_lap.get_car_data().add_distance()

# ---------------------------------
# VITESSE
# ---------------------------------
fig_speed = px.line(
    telemetry,
    x="Distance",
    y="Speed",
    title=f"Vitesse - Tour rapide {selected_driver}"
)

st.plotly_chart(
    fig_speed,
    use_container_width=True
)

# ---------------------------------
# TRACK MAP
# ---------------------------------
st.subheader("🗺️ Circuit Map")

pos_data = fastest_lap.get_pos_data()

telemetry["X"] = pos_data["X"]
telemetry["Y"] = pos_data["Y"]

fig_track = px.scatter(
    telemetry,
    x="X",
    y="Y",
    color="Speed",
    title=f"Track Map - {selected_driver}",
    color_continuous_scale="Turbo"
)

fig_track.update_traces(
    marker=dict(size=5)
)

fig_track.update_layout(
    height=700
)

st.plotly_chart(
    fig_track,
    use_container_width=True
)

# ---------------------------------
# THROTTLE
# ---------------------------------
fig_throttle = px.line(
    telemetry,
    x="Distance",
    y="Throttle",
    title=f"Throttle - {selected_driver}"
)

st.plotly_chart(
    fig_throttle,
    use_container_width=True
)

# ---------------------------------
# BRAKE
# ---------------------------------
fig_brake = px.line(
    telemetry,
    x="Distance",
    y="Brake",
    title=f"Freinage - {selected_driver}"
)

st.plotly_chart(
    fig_brake,
    use_container_width=True
)

# ---------------------------------
# FOOTER
# ---------------------------------
st.markdown("---")
st.caption("Built by Yanis • AI Motorsport Analytics")