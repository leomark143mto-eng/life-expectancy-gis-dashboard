import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from io import BytesIO

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="Life Expectancy GIS-SD Dashboard",
    layout="wide"
)

# ==================================
# LOAD DATA
# ==================================

GIS = pd.read_excel(
    "GIS_POLICY_PROJECTIONS.xlsx"
)

SD = pd.read_excel(
    "SD_MASTER.xlsx"
)

# ==================================
# HEADER LOGOS
# ==================================

c1,c2,c3,c4,c5 = st.columns([1,1.5,1.5,1.5,1])

with c2:
    st.image(
        "logo1.png.jpg",
        width=140
    )

with c3:
    st.image(
        "logo2.png.png",
        width=140
    )

with c4:
    st.image(
        "logo3.png.jpg",
        width=140
    )

# ==================================
# HEADER
# ==================================

st.title(
    "Life Expectancy Inequalities Decision Support System"
)

st.markdown(
    """
    ### GIS and System Dynamics-Based Policy Planning Tool

    Province of Agusan del Sur
    """
)

# ==================================
# SIDEBAR
# ==================================

st.sidebar.title(
     "Decision Support Controls"
)

scenario = st.sidebar.selectbox(
    "Select Scenario",
    [
        "LEII",
        "LEII_Income",
        "LEII_Education",
        "LEII_Hypertension",
        "LEII_Combined",
        "LEII_2030",
        "LEII_2040",
        "LEII_2050"
    ]
)

selected_municipality = st.sidebar.selectbox(
    "Select Municipality",
    GIS["Municipality"].tolist()
)


# ==================================
# POLICY SIMULATOR
# ==================================

st.sidebar.markdown("---")
st.sidebar.subheader("Policy Simulator")

income_boost = st.sidebar.slider(
    "Income Improvement (%)",
    0, 50, 0
)

education_boost = st.sidebar.slider(
    "Education Improvement (%)",
    0, 50, 0
)

health_boost = st.sidebar.slider(
    "Health Access Improvement (%)",
    0, 50, 0
)

hypertension_reduction = st.sidebar.slider(
    "Hypertension Reduction (%)",
    0, 50, 0
)


# ==================================
# KPI
# ==================================


m1,m2,m3 = st.columns(3)

m1.metric(
    "Municipalities",
    len(GIS)
)

m2.metric(
    "Highest LEII",
    round(
        GIS["LEII"].max(),
        2
    )
)

m3.metric(
    "Average LEII",
    round(
        GIS["LEII"].mean(),
        2
    )
)

# ==========================
# EXECUTIVE SUMMARY
# ==========================

highest_muni = GIS.loc[
    GIS["LEII"].idxmax(),
    "Municipality"
]

lowest_muni = GIS.loc[
    GIS["LEII"].idxmin(),
    "Municipality"
]

st.info(
    f"""
    Executive Summary

    The province consists of {len(GIS)} municipalities.
    The highest Life Expectancy Inequality Index (LEII)
    was recorded in {highest_muni}, while the lowest
    was observed in {lowest_muni}.

    The average provincial LEII is
    {GIS['LEII'].mean():.3f}. This dashboard integrates
    GIS mapping, System Dynamics simulation, and policy
    analysis to support evidence-based decision making
    for life expectancy improvement in Agusan del Sur.
    """
)


# ==================================
# TABS
# ==================================
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs(
    [
        "Historical Trends",
        "GIS Map",
        "Rankings",
        "System Dynamics",
        "Municipality Profile",
        "Scenario Comparison",
        "Policy Recommendations"
    ]
)


# ==================================
# TAB 1
# ==================================

with tab1:

    st.header(
        "Life Expectancy Trend"
    )

    fig = px.line(
        SD,
        x="Year",
        y="Life Expectancy percentage (at birth)",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================
# TAB 2
# ==================================

with tab2:

    st.header(
        "Municipal LEII Map"
    )

    # ==========================
    # YEAR SLIDER
    # ==========================

    selected_year = st.slider(
        "Projection Year",
        2025,
        2050,
        2025
    )

    growth_factor = (
        selected_year - 2025
    ) * 0.01

    # ==========================
    # PROJECTED DATA
    # ==========================

    projected_records = []

    for _, row in GIS.iterrows():

        policy_effect = (
            income_boost * 0.002 +
            education_boost * 0.002 +
            health_boost * 0.002 +
            hypertension_reduction * 0.003
        )

        value = min(
            1,
            row[scenario]
            + growth_factor
            + policy_effect
        )

        projected_population = int(
            row["Population"]
            *
            (1.015 ** (selected_year - 2025))
        )

        projected_records.append(
            {
                "Municipality":
                row["Municipality"],

                "Population":
                projected_population,

                scenario:
                value
            }
        )

    projected_df = pd.DataFrame(
        projected_records
    )

    # ==========================
    # EXECUTIVE SUMMARY
    # ==========================

    highest_muni = projected_df.loc[
        projected_df[scenario].idxmax(),
        "Municipality"
    ]

    lowest_muni = projected_df.loc[
        projected_df[scenario].idxmin(),
        "Municipality"
    ]

    avg_2050 = round(
        projected_df[scenario].mean(),
        3
    )

    total_pop = int(
        projected_df["Population"].sum()
    )

    e1,e2,e3,e4 = st.columns(4)

    e1.metric(
        "Highest Municipality",
        highest_muni
    )

    e2.metric(
        "Lowest Municipality",
        lowest_muni
    )

    e3.metric(
        "Average LEII",
        avg_2050
    )

    e4.metric(
        "Projected Population",
        f"{total_pop:,}"
    )

    # ==========================
    # MAP
    # ==========================

    m = folium.Map(
        location=[8.5,125.9],
        zoom_start=9
    )

    for _, row in GIS.iterrows():

        policy_effect = (
            income_boost * 0.002 +
            education_boost * 0.002 +
            health_boost * 0.002 +
            hypertension_reduction * 0.003
        )

        value = min(
            1,
            row[scenario]
            + growth_factor
            + policy_effect
        )

        projected_population = int(
            row["Population"]
            *
            (1.015 ** (selected_year - 2025))
        )

        if value >= 0.70:
            color = "green"

        elif value >= 0.40:
            color = "orange"

        else:
            color = "red"

        popup_html = f"""
        <h4>{row['Municipality']}</h4>

        Population ({selected_year}):

        {projected_population:,}

        <br><br>

        Health Access:

        {row['Health_Access']:.3f}

        <br><br>

        Current LEII:

        {row['LEII']:.3f}

        <br><br>

        Projected Scenario:

        {value:.3f}

        <br><br>

        Policy Effect:

        {policy_effect:.3f}

        <br><br>

        Category:

        {'High' if value >= 0.70 else 'Moderate' if value >= 0.40 else 'Low'}
        """

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
            popup=folium.Popup(
                popup_html,
                max_width=350
            )
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=600
    )

    # ==========================
    # PROJECTED RANKING
    # ==========================

    st.subheader(
        f"Projected Ranking ({selected_year})"
    )

    ranking = projected_df.sort_values(
        scenario,
        ascending=False
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

    
    # ==========================
    # EXPORT CSV
    # ==========================

    csv = ranking.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Ranking CSV",
        data=csv,
        file_name=f"{scenario}_{selected_year}.csv",
        mime="text/csv"
    )
    
    # ==========================
    # EXPORT EXCEL
    # ==========================

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        ranking.to_excel(
             writer,
             index=False,
             sheet_name="Ranking"
        )

    st.download_button(
        label="📊 Download Ranking Excel",
        data=excel_buffer.getvalue(),
        file_name=f"{scenario}_{selected_year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    
    # ==========================
    # TOP / BOTTOM
    # ==========================

    col1,col2 = st.columns(2)

    with col1:

        st.subheader(
            "Top 3 Municipalities"
        )

        st.dataframe(
            ranking.head(3),
            use_container_width=True
        )

    with col2:

        st.subheader(
            "Bottom 3 Municipalities"
        )

        st.dataframe(
            ranking.tail(3),
            use_container_width=True
        )

    # ==========================
    # BAR CHART
    # ==========================

    fig_rank = px.bar(
        ranking,
        x="Municipality",
        y=scenario,
        color=scenario,
        title=f"{scenario} Projection ({selected_year})"
    )

    st.plotly_chart(
        fig_rank,
        use_container_width=True
    )

    
# ==================================
# TAB 3
# ==================================

with tab3:

    st.header(
        "Municipality Rankings"
    )

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
        use_container_width=True
    )

    fig2 = px.bar(
        ranking,
        x="Municipality",
        y=scenario
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    
# ==================================
# TAB 4
# ==================================

with tab4:

    st.header(
        "Life Expectancy Projection"
    )

    projection = []

    life_expectancy = 57.35

    # ==========================
    # VENSIM-LIKE POLICY EFFECTS
    # ==========================

    income_index = (
        income_boost / 50
    )

    education_index = (
        education_boost / 50
    )

    health_index = (
        health_boost / 50
    )

    hypertension_index = (
        hypertension_reduction / 50
    )

    # Improvement Equation

    improvement = (
        (0.30 * income_index)
        +
        (0.30 * education_index)
        +
        (0.20 * health_index)
        +
        0.20
    )

    # Decline Equation

    decline = (
        0.15
        -
        (0.10 * hypertension_index)
    )

    # ==========================
    # YEARLY PROJECTION
    # ==========================

    for y in range(2025, 2051):

        life_expectancy += (
            improvement - decline
        )

        projection.append(
            [
                y,
                round(
                    life_expectancy,
                    2
                )
            ]
        )

    # ==========================
    # DATAFRAME
    # ==========================

    proj_df = pd.DataFrame(
        projection,
        columns=[
            "Year",
            "Life Expectancy"
        ]
    )

    # ==========================
    # GRAPH
    # ==========================

    fig_sd = px.line(
        proj_df,
        x="Year",
        y="Life Expectancy",
        markers=True,
        title=f"{scenario} Projection (2025-2050)"
    )

    st.plotly_chart(
        fig_sd,
        use_container_width=True
    )

    # ==========================
    # INDICATORS
    # ==========================

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Improvement Rate",
        round(
            improvement,
            3
        )
    )

    c2.metric(
        "Decline Rate",
        round(
            decline,
            3
        )
    )

    c3.metric(
        "2050 Projection",
        round(
            proj_df[
                "Life Expectancy"
            ].iloc[-1],
            2
        )
    )

    # ==========================
    # TABLE
    # ==========================

    st.dataframe(
        proj_df,
        use_container_width=True
    )

    
# ==================================
# TAB 5
# ==================================

with tab5:

    st.header(
        "Municipality Life Expectancy Profile"
    )

    muni = GIS[
        GIS["Municipality"]
        ==
        selected_municipality
    ].iloc[0]

    st.subheader(
        selected_municipality
    )

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "Population",
        f"{int(muni['Population']):,}"
    )

    c2.metric(
        "Health Access",
        round(
            muni["Health_Access"],
            3
        )
    )

    c3.metric(
        "LEII",
        round(
            muni["LEII"],
            3
        )
    )

    c4.metric(
        "Scenario",
        scenario
    )

    # ==========================
    # MUNICIPAL SD PARAMETERS
    # ==========================

    leii_factor = muni["LEII"]

    health_factor = (
        muni["Health_Access"]
    )

    policy_effect = (
        income_boost * 0.002 +
        education_boost * 0.002 +
        health_boost * 0.002 +
        hypertension_reduction * 0.003
    )

    # ==========================
    # STARTING LIFE EXPECTANCY
    # ==========================

    life_expectancy = (
        57.35
        +
        (leii_factor * 10)
        +
        (health_factor * 5)
    )

    projection = []

    # ==========================
    # MUNICIPAL PROJECTION
    # ==========================

    for year in range(
        2025,
        2051
    ):

        improvement = (
            0.15 +
            (leii_factor * 0.15) +
            (health_factor * 0.10) +
            policy_effect
        )

        decline = (
            0.10 -
            (
                hypertension_reduction
                * 0.001
            )
        )

        life_expectancy += (
            improvement -
            decline
        )

        projected_population = int(
            muni["Population"]
            *
            (
                1.015 **
                (year - 2025)
            )
        )

        projection.append(
            [
                year,
                round(
                    life_expectancy,
                    2
                ),
                projected_population
            ]
        )

    muni_df = pd.DataFrame(
        projection,
        columns=[
            "Year",
            "Life Expectancy",
            "Population"
        ]
    )

    # ==========================
    # GRAPH
    # ==========================

    fig_muni = px.line(
        muni_df,
        x="Year",
        y="Life Expectancy",
        markers=True,
        title=f"{selected_municipality} Projection"
    )

    st.plotly_chart(
        fig_muni,
        use_container_width=True
    )

    # ==========================
    # FINAL 2050 KPIs
    # ==========================

    c1,c2 = st.columns(2)

    c1.metric(
        "2050 Life Expectancy",
        round(
            muni_df[
                "Life Expectancy"
            ].iloc[-1],
            2
        )
    )

    c2.metric(
        "2050 Population",
        f"{int(muni_df['Population'].iloc[-1]):,}"
    )

    # ==========================
    # TABLE
    # ==========================

    st.dataframe(
        muni_df,
        use_container_width=True
    )
    

# ==================================
# TAB 6
# ==================================

with tab6:

    st.header(
        "Scenario Comparison"
    )

    years = list(
        range(2025, 2051)
    )

    baseline = []
    income = []
    education = []
    hypertension = []
    combined = []

    le_base = 57.35
    le_income = 57.35
    le_education = 57.35
    le_hypertension = 57.35
    le_combined = 57.35

    for y in years:

        le_base += 0.20
        baseline.append(le_base)

        le_income += 0.30
        income.append(le_income)

        le_education += 0.27
        education.append(le_education)

        le_hypertension += 0.23
        hypertension.append(le_hypertension)

        le_combined += 0.40
        combined.append(le_combined)

    compare_df = pd.DataFrame(
        {
            "Year": years,
            "Baseline": baseline,
            "Income Policy": income,
            "Education Policy": education,
            "Hypertension Policy": hypertension,
            "Combined Policy": combined
        }
    )

    fig_compare = px.line(
        compare_df,
        x="Year",
        y=[
            "Baseline",
            "Income Policy",
            "Education Policy",
            "Hypertension Policy",
            "Combined Policy"
        ],
        markers=True
    )

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

    st.dataframe(
        compare_df,
        use_container_width=True
    )


# ==================================
# TAB 7
# ==================================

with tab7:

    st.header(
        "Policy Recommendation Engine"
    )

    muni = GIS[
        GIS["Municipality"]
        ==
        selected_municipality
    ].iloc[0]

    st.subheader(
        f"Municipality: {selected_municipality}"
    )

    leii = muni["LEII"]
    health = muni["Health_Access"]

    # ==========================
    # RECOMMENDATION LOGIC
    # ==========================

    recommendations = []

    if leii < 0.40:

        recommendations.append(
            "High priority municipality. Immediate intervention recommended."
        )

    if health < 0.60:

        recommendations.append(
            "Improve healthcare accessibility and health service coverage."
        )

    if income_boost < 20:

        recommendations.append(
            "Strengthen income-generating and livelihood programs."
        )

    if education_boost < 20:

        recommendations.append(
            "Expand education access and retention initiatives."
        )

    if hypertension_reduction < 20:

        recommendations.append(
            "Implement hypertension screening and prevention programs."
        )

    if len(recommendations) == 0:

        recommendations.append(
            "Current policy settings are favorable. Maintain integrated interventions."
        )

    # ==========================
    # DISPLAY
    # ==========================

    for rec in recommendations:

        st.success(rec)

    # ==========================
    # OVERALL PRIORITY
    # ==========================

    if leii >= 0.70:

        priority = "LOW PRIORITY"

    elif leii >= 0.40:

        priority = "MODERATE PRIORITY"

    else:

        priority = "HIGH PRIORITY"

    st.metric(
        "Priority Classification",
        priority
    )


st.markdown("---")

st.caption(
    "Life Expectancy Inequalities DSS | GIS + System Dynamics | Agusan del Sur | 2026"
)
