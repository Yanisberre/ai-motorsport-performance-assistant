import streamlit as st
import fastf1
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Motorsport Performance Assistant",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# PREMIUM CSS
# ---------------------------------------------------
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background: linear-gradient(
        180deg,
        #0B0F14 0%,
        #111827 100%
    );
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4 {
    color: white;
}

[data-testid="stMetric"] {

    background: linear-gradient(
        145deg,
        #161B22,
        #1F2630
    );

    border: 1px solid #30363D;

    padding: 25px;

    border-radius: 20px;

    text-align: center;

    box-shadow:
        0px 0px 20px rgba(255,255,255,0.05);

    transition: 0.3s;
}

[data-testid="stMetric"]:hover {

    transform: translateY(-3px);

    border: 1px solid #FF1801;
}

.stPlotlyChart {

    background-color: #161B22;

    padding: 20px;

    border-radius: 20px;

    box-shadow:
        0px 0px 20px rgba(255,255,255,0.03);
}

section[data-testid="stSidebar"] {

    background: linear-gradient(
        180deg,
        #11161C 0%,
        #0E1117 100%
    );
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HERO HEADER
# ---------------------------------------------------
col_logo, col_title = st.columns([1, 5])

with col_logo:

    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/d/d1/F1.svg",
        width=120
    )

with col_title:

    st.markdown("""
    # 🏎️ AI Motorsport Performance Assistant
    
    ### Premium Formula 1 Analytics Platform
    
    Telemetry • Delta Analysis • Track Intelligence • Motorsport Data
    """)

st.markdown("---")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:

    st.markdown("## ⚙️ Race Configuration")

    year = st.selectbox(
        "Season",
        [2024, 2023, 2022]
    )

    grand_prix = st.selectbox(
        "Grand Prix",
        [
            "Monaco",
            "Silverstone",
            "Monza",
            "Spa",
            "Suzuka",
            "Interlagos"
        ]
    )

    session_type = st.selectbox(
        "Session",
        ["R", "Q", "FP1"]
    )

# ---------------------------------------------------
# NAVIGATION BAR
# ---------------------------------------------------
selected = option_menu(
    menu_title=None,
    options=[
        "Overview",
        "Comparison",
        "Telemetry",
        "Track Map",
        "Tyre Strategy"
    ],
    icons=[
        "speedometer2",
        "bar-chart",
        "activity",
        "map",
        "circle"
    ],
    orientation="horizontal"
)

# ---------------------------------------------------
# LOAD SESSION
# ---------------------------------------------------
@st.cache_data(show_spinner=False)
def load_session(year, grand_prix, session_type):

    session = fastf1.get_session(
        year,
        grand_prix,
        session_type
    )

    session.load()

    return session

with st.spinner("Loading F1 Data..."):

    session = load_session(
        year,
        grand_prix,
        session_type
    )

# ---------------------------------------------------
# RESULTS DATAFRAME
# ---------------------------------------------------
results = session.results

df = results[[
    "Abbreviation",
    "TeamName",
    "Position",
    "Points"
]]

df.columns = [
    "Driver",
    "Team",
    "Position",
    "Points"
]

# ---------------------------------------------------
# OVERVIEW PAGE
# ---------------------------------------------------
if selected == "Overview":

    st.subheader("🏁 Race Overview")

    winner = df.iloc[0]["Driver"]

    fastest_lap = session.laps.pick_fastest()

    fastest_time = fastest_lap[
        "LapTime"
    ].total_seconds()

    avg_speed = fastest_lap.get_car_data()[
        "Speed"
    ].mean()

    total_laps = session.total_laps

    # KPI CARDS
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            "🏆 Winner",
            winner
        )

    with kpi2:
        st.metric(
            "🚀 Avg Speed",
            f"{avg_speed:.0f} km/h"
        )

    with kpi3:
        st.metric(
            "⏱️ Fastest Lap",
            f"{fastest_time:.2f}s"
        )

    with kpi4:
        st.metric(
            "📍 Total Laps",
            total_laps
        )

    st.markdown("---")

    # RESULTS TABLE
    st.subheader("📊 Race Results")

    st.dataframe(
        df,
        use_container_width=True
    )

    # GRAPH
    fig_points = px.bar(
        df,
        x="Driver",
        y="Points",
        color="Team",
        title="Driver Points"
    )

    fig_points.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_points,
        use_container_width=True
    )

# ---------------------------------------------------
# COMPARISON PAGE
# ---------------------------------------------------
elif selected == "Comparison":

    st.subheader("⚔️ Driver Comparison")

    col1, col2 = st.columns(2)

    with col1:

        driver_1 = st.selectbox(
            "Driver 1",
            df["Driver"],
            index=0
        )

    with col2:

        driver_2 = st.selectbox(
            "Driver 2",
            df["Driver"],
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

    # KPI CARDS
    stat1, stat2, stat3, stat4 = st.columns(4)

    with stat1:
        st.metric(
            f"🏎️ Best Lap {driver_1}",
            f"{laps_1['LapTimeSeconds'].min():.2f}s"
        )

    with stat2:
        st.metric(
            f"🏎️ Best Lap {driver_2}",
            f"{laps_2['LapTimeSeconds'].min():.2f}s"
        )

    with stat3:
        st.metric(
            f"📈 Avg Pace {driver_1}",
            f"{laps_1['LapTimeSeconds'].mean():.2f}s"
        )

    with stat4:
        st.metric(
            f"📈 Avg Pace {driver_2}",
            f"{laps_2['LapTimeSeconds'].mean():.2f}s"
        )

    laps_1["Driver"] = driver_1
    laps_2["Driver"] = driver_2

    comparison_df = pd.concat([
        laps_1,
        laps_2
    ])

    # COMPARISON GRAPH
    fig_compare = px.line(
        comparison_df,
        x="LapNumber",
        y="LapTimeSeconds",
        color="Driver",
        title=f"{driver_1} vs {driver_2}"
    )

    fig_compare.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

    # DELTA ANALYSIS
    st.subheader("⏳ Delta Time Analysis")

    delta_df = pd.merge(
        laps_1[["LapNumber", "LapTimeSeconds"]],
        laps_2[["LapNumber", "LapTimeSeconds"]],
        on="LapNumber",
        suffixes=(f"_{driver_1}", f"_{driver_2}")
    )

    delta_df["Delta"] = (
        delta_df[f"LapTimeSeconds_{driver_1}"]
        - delta_df[f"LapTimeSeconds_{driver_2}"]
    )

    fig_delta = px.line(
        delta_df,
        x="LapNumber",
        y="Delta",
        title=f"Delta Time {driver_1} vs {driver_2}"
    )

    fig_delta.update_layout(
        template="plotly_dark"
    )

    fig_delta.add_hline(
        y=0,
        line_dash="dash"
    )

    st.plotly_chart(
        fig_delta,
        use_container_width=True
    )

# ---------------------------------------------------
# TELEMETRY PAGE
# ---------------------------------------------------
elif selected == "Telemetry":

    st.subheader("📡 Telemetry Analysis")

    selected_driver = st.selectbox(
        "Choose Driver",
        df["Driver"]
    )

    driver_laps = session.laps.pick_drivers(
        selected_driver
    )

    fastest_lap = driver_laps.pick_fastest()

    telemetry = fastest_lap.get_car_data().add_distance()

    # SPEED GRAPH
    fig_speed = px.line(
        telemetry,
        x="Distance",
        y="Speed",
        title=f"Speed Trace - {selected_driver}"
    )

    fig_speed.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_speed,
        use_container_width=True
    )

    # THROTTLE GRAPH
    fig_throttle = px.line(
        telemetry,
        x="Distance",
        y="Throttle",
        title=f"Throttle Trace - {selected_driver}"
    )

    fig_throttle.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_throttle,
        use_container_width=True
    )

    # BRAKE GRAPH
    fig_brake = px.line(
        telemetry,
        x="Distance",
        y="Brake",
        title=f"Brake Trace - {selected_driver}"
    )

    fig_brake.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_brake,
        use_container_width=True
    )

# ---------------------------------------------------
# TRACK MAP PAGE
# ---------------------------------------------------
elif selected == "Track Map":

    st.subheader("🗺️ Track Map")

    selected_driver = st.selectbox(
        "Choose Driver",
        df["Driver"]
    )

    driver_laps = session.laps.pick_drivers(
        selected_driver
    )

    fastest_lap = driver_laps.pick_fastest()

    telemetry = fastest_lap.get_car_data().add_distance()

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
        template="plotly_dark",
        height=700
    )

    st.plotly_chart(
        fig_track,
        use_container_width=True
    )

# ---------------------------------------------------
# TYRE STRATEGY PAGE
# ---------------------------------------------------
elif selected == "Tyre Strategy":

    st.subheader("🛞 Tyre Strategy Analysis")

    laps = session.laps

    stints = laps[[
        "Driver",
        "Stint",
        "Compound",
        "LapNumber"
    ]]

    stints = stints.groupby([
        "Driver",
        "Stint",
        "Compound"
    ]).count().reset_index()

    stints = stints.rename(
        columns={"LapNumber": "StintLength"}
    )

    fig_stints = px.bar(
        stints,
        x="Driver",
        y="StintLength",
        color="Compound",
        title="Tyre Strategy"
    )

    fig_stints.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_stints,
        use_container_width=True
    )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")

st.caption(
    "Built by Yanis • AI Motorsport Analytics"
)