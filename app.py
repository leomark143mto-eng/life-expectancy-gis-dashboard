import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Life Expectancy Dashboard",
    layout="wide"
)

# ==================================================
# LOAD DATA
# ==================================================

GIS = pd.read_excel("GIS_POLICY_PROJECTIONS.xlsx")
SD = pd.read_excel("SD_MASTER.xlsx")

# ==================================================
# HEADER
# ==================================================

st.title("Mapping and Modeling Life Expectancy Inequalities")
st.subheader("System Dynamics - GIS Prototype")

# ==================================================
# SIDEBAR
# ==================================================

scenario = st.sidebar.selectbox(
    "Select Scenario",
    [
        "LEII",
        "LEII_2030",
        "LEII_2040",
        "LEII_2050"
    ]
)

# ==================================================
# KPIs
# ==================================================

c1, c2, c3 = st.columns(3)

c1.metric(
    "Municipalities",
    len(GIS)
)

c2.metric(
    "Highest LEII",
    round(GIS["LEII"].max(),3)
)

c3.metric(
    "Average LEII",
    round(GIS["LEII"].mean(),3)
)

# ==================================================
# TABS
# ==================================================

tab1, tab2, tab3 = st.tabs(
    [
        "Historical Trends",
        "GIS Map",
        "Rankings"
    ]
)

# ==================================================
# TAB 1
# ==================================================

with tab1:

    st.header("Life Expectancy Trend")

    fig = px.line(
        SD,
        x="Year",
        y="Life Expectancy percentage (at birth)",
        markers=True
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# ==================================================
# TAB 2
# ==================================================

with tab2:

    st.header("Municipal LEII Map")

    m = folium.Map(
        location=[8.45,125.85],
        zoom_start=9
    )

    for _, row in GIS.iterrows():

        value = row[scenario]

        if value >= 0.70:
            color = "green"

        elif value >= 0.40:
            color = "orange"

        else:
            color = "red"

        folium.CircleMarker(
            location=[
                row["Latitude"],
                row["Longitude"]
            ],
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=f"""
            {row['Municipality']}
            <br>LEII = {value:.3f}
            """
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=600
    )

# ==================================================
# TAB 3
# ==================================================

with tab3:

    st.header("Municipality Rankings")

    ranking = GIS[
        [
            "Municipality",
            scenario
        ]
    ].sort_values(
        scenario,
        ascending=False
    )

    st.dataframe(
        ranking,
        width="stretch"
    )

    fig2 = px.bar(
        ranking,
        x="Municipality",
        y=scenario
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )