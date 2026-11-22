"""
CosmosVis - Global Space Missions & Satellite Tracker
M.Sc. Computer Science Interactive Visual Analytics Mini-Project.

Transforming authentic historical orbital data into interactive visual intelligence.
Operates exclusively on real user-uploaded Kaggle space mission records (Space_Corrected.csv).
Zero synthetic or fabricated data.

Tech Stack: Python, Streamlit, Pandas, NumPy, Plotly, Geopy.
"""

import streamlit as st
import pandas as pd
import numpy as np

# Page configuration - Must be the first Streamlit command
st.set_page_config(
    page_title="CosmosVis — Global Space Missions & Satellite Tracker",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Internal module imports (built purely with approved technologies)
import data_loader
import charts
import utils


# ==============================================================================
# SIDEBAR: DATA INGESTION & TELEMETRY CONTROLS
# ==============================================================================
df_full = None
metadata = None
error_msg = None

with st.sidebar:
    st.title("🛰️ CosmosVis")
    st.caption("Global Space Missions & Satellite Tracker")
    st.markdown("---")

    st.subheader("📂 Space Missions CSV Data")
    st.caption("Upload your Kaggle `Space_Corrected.csv` dataset to populate the dashboard with authentic data.")

    # Exactly one CSV uploader in the application
    sidebar_uploaded_file = st.file_uploader(
        "Upload Space Missions CSV",
        type=["csv"],
        help="Upload Kaggle 'All Space Missions from 1957' (Space_Corrected.csv)",
        key="sidebar_csv_uploader",
    )
    st.markdown("---")

# Process uploaded data (strictly user-uploaded only, no bundled or default dataset)
if sidebar_uploaded_file is not None:
    df_full, metadata, error_msg = data_loader.load_dataset_from_source(sidebar_uploaded_file)


# ==============================================================================
# WELCOME / UPLOAD SCREEN (WHEN NO CSV IS LOADED)
# ==============================================================================
if df_full is None:
    if error_msg:
        st.error(f"⚠️ **Dataset Validation Failed:**\n\n{error_msg}")

    st.title("🚀 Welcome to CosmosVis!")
    st.markdown(
        "A comprehensive visual analytics platform for exploring global orbital spaceflights, "
        "spaceport telemetry, national reliability benchmarks, and rocketry economics."
    )

    st.info(
        "👈 **To Get Started:** Please upload your Kaggle `Space_Corrected.csv` dataset using the "
        "**📂 Space Missions CSV Data** file uploader in the left sidebar."
    )

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📋 Dataset Requirements & Information")
        st.markdown(
            """
            CosmosVis is designed to analyze the authentic **Kaggle Space Missions Dataset**:

            - **Dataset Name:** *All Space Missions from 1957*
            - **Dataset Source:** [Kaggle Space Exploration Dataset](https://www.kaggle.com/datasets/agirlcoding/all-space-missions-from-1957)
            - **Expected Filename:** `Space_Corrected.csv`
            - **Historical Span:** October 1957 (Sputnik 1) to August 2020 (4,324 launches)
            - **Geographic Coverage:** 38 verified orbital spaceports worldwide (WGS-84 ellipsoidal coordinates)
            - **Academic Context:** Developed as an interactive M.Sc. Computer Science visual analytics mini-project

            *Authenticity Standard: CosmosVis computes all metrics directly from user-uploaded records. No synthetic, fake, or fallback records are generated.*
            """
        )

    with col_right:
        st.subheader("📊 Mandatory Column Schema")
        st.markdown(
            """
            The uploaded CSV must contain the following 7 standard Kaggle columns:

            | Column Name | Description & Example |
            | :--- | :--- |
            | `Company Name` | Aerospace agency or contractor (*NASA, SpaceX, Roscosmos, ISRO, CASC*) |
            | `Location` | Launch pad facility and country (*LC-39A, Kennedy Space Center, USA*) |
            | `Datum` | UTC launch date & timestamp (*Fri Aug 07, 2020 05:12 UTC*) |
            | `Detail` | Rocket vehicle & payload (*Falcon 9 Block 5 | Starlink V1 L9*) |
            | `Status Rocket` | Operational vehicle status (*StatusActive*, *StatusRetired*) |
            | `Rocket` | Disclosed launch cost in Millions USD ($M) (*e.g., 50.0*) |
            | `Status Mission` | Flight outcome (*Success*, *Failure*, *Partial Failure*) |
            """
        )

    st.markdown("---")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown("#### 📈 1. Historical Timeline")
        st.markdown(
            "Track orbital launch frequency across 7 historical decades, "
            "from the early Space Race to modern commercial megaconstellations."
        )
    with col_f2:
        st.markdown("#### 🎯 2. Flight Reliability")
        st.markdown(
            "Explore multi-level hierarchical Sunburst and Treemap visualizations, "
            "national reliability benchmarks, and 70-year success curves."
        )
    with col_f3:
        st.markdown("#### 🗺️ 3. Spaceport Geodesics")
        st.markdown(
            "Interactive world map of 38 verified launch centers with Geopy "
            "great-circle distance and Earth rotation assist velocity calculations."
        )

    st.stop()


# ==============================================================================
# SIDEBAR FILTERS (ACTIVE ONCE AUTHENTIC DATA IS UPLOADED)
# ==============================================================================
with st.sidebar:
    st.subheader("🛰️ Mission Telemetry Filters")
    st.caption("Apply dynamic multi-dimensional filters across all visual engines.")

    # 1. Year Window Slider
    min_year = metadata["min_year"]
    max_year = metadata["max_year"]
    selected_year_range = st.slider(
        "📅 Launch Year Window",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        help="Filter missions across the historical timeline.",
    )

    # 2. Country Multiselect (empty list = all countries)
    all_countries = metadata["unique_countries"]
    selected_countries = st.multiselect(
        "🌍 Spacefaring Nations",
        options=all_countries,
        default=[],
        placeholder="All Nations (select to filter)...",
        help="Filter by sovereign nation. Leave empty to include all.",
    )

    # 3. Aerospace Company Multiselect (empty list = all companies)
    all_companies = metadata["unique_companies"]
    selected_companies = st.multiselect(
        "🏢 Aerospace Companies",
        options=all_companies,
        default=[],
        placeholder="All Operators (select to filter)...",
        help="Filter by launch operator. Leave empty to include all.",
    )

    # 4. Mission Outcome Multiselect (empty list = all outcomes)
    all_statuses = sorted(df_full["Mission_Status"].unique().tolist())
    selected_statuses = st.multiselect(
        "🎯 Mission Outcome",
        options=all_statuses,
        default=[],
        placeholder="All Outcomes (select to filter)...",
        help="Filter by flight mission success or anomaly. Leave empty to include all.",
    )

    # 5. Rocket Fleet Status Radio
    status_choice = st.radio(
        "🚀 Rocket Fleet Status",
        options=["All Statuses", "Active Only", "Retired Only"],
        index=0,
        horizontal=True,
    )

    st.markdown("---")
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()

    st.caption(
        f"**CosmosVis Telemetry Engine**\n\n"
        f"• Authentic Records: {len(df_full):,} Launches\n\n"
        f"• Active Spaceports: {len(metadata['unique_spaceports'])} Real Spaceports\n\n"
        f"• Geodesic Engine: WGS-84 / Geopy\n\n"
        f"• Timeline: {min_year} – {max_year}"
    )


# ==============================================================================
# BIDIRECTIONAL REACTIVE FILTERING PIPELINE
# ==============================================================================
df_filtered = df_full[
    (df_full["Year"] >= selected_year_range[0])
    & (df_full["Year"] <= selected_year_range[1])
].copy()

# Empty list [] in multiselect means NO filter applied (shows all)
if selected_countries:
    df_filtered = df_filtered[df_filtered["Country"].isin(selected_countries)]

if selected_companies:
    df_filtered = df_filtered[df_filtered["Company_Name"].isin(selected_companies)]

if selected_statuses:
    df_filtered = df_filtered[df_filtered["Mission_Status"].isin(selected_statuses)]

if status_choice == "Active Only":
    df_filtered = df_filtered[df_filtered["Rocket_Status"] == "Active"]
elif status_choice == "Retired Only":
    df_filtered = df_filtered[df_filtered["Rocket_Status"] == "Retired"]


# ==============================================================================
# HEADER BANNER & CORE OBJECTIVES
# ==============================================================================
st.title("CosmosVis — Global Space Missions & Satellite Tracker")
st.caption(
    "Transforming Authentic Historical Orbital Data into Interactive Visual Intelligence | "
    "M.Sc. Computer Science Mini-Project"
)

st.markdown(
    "🎯 **Objective 1:** Historical Timeline | "
    "🌐 **Objective 2:** Reliability Benchmarks | "
    "💰 **Objective 3:** Fleet Economics | "
    "🗺️ **Objective 4:** Spaceport Geodesics | "
    "🔍 **Objective 5:** Mission Search"
)
st.markdown("---")


# ==============================================================================
# DYNAMIC TOP-LEVEL KPI METRICS (ST.METRIC)
# ==============================================================================
total_missions_filtered = len(df_filtered)
if total_missions_filtered > 0:
    success_rate_filtered = (df_filtered["Mission_Status"] == "Success").mean() * 100
    unique_countries_filtered = df_filtered["Country"].nunique()
    unique_companies_filtered = df_filtered["Company_Name"].nunique()
    costed_count = int(df_filtered["Has_Cost_Data"].sum())
    costed_pct = (costed_count / total_missions_filtered) * 100
else:
    success_rate_filtered = 0.0
    unique_countries_filtered = 0
    unique_companies_filtered = 0
    costed_count = 0
    costed_pct = 0.0

col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5)
with col_k1:
    st.metric(
        label="🚀 Total Missions",
        value=f"{total_missions_filtered:,}",
        help=f"Missions launched within {selected_year_range[0]} – {selected_year_range[1]} window",
    )
with col_k2:
    st.metric(
        label="🎯 Mission Success Rate",
        value=f"{success_rate_filtered:.1f}%",
        help="Overall flight reliability index for filtered missions",
    )
with col_k3:
    st.metric(
        label="🌐 Spacefaring Nations",
        value=f"{unique_countries_filtered}",
        help="Sovereign operators conducting orbital launches",
    )
with col_k4:
    st.metric(
        label="🏢 Active Companies",
        value=f"{unique_companies_filtered}",
        help="Aerospace agencies and commercial contractors",
    )
with col_k5:
    st.metric(
        label="💰 Disclosed Cost Records",
        value=f"{costed_count:,}",
        help=f"{costed_pct:.1f}% of filtered flights have authentic reported cost telemetry",
    )

st.markdown("---")


# ==============================================================================
# DYNAMIC AUTOMATED INSIGHTS GENERATION
# ==============================================================================
def generate_dynamic_insights(df: pd.DataFrame) -> str:
    """Computes automated intelligence text based purely on authentic records."""
    if df.empty:
        return "No mission telemetry records correspond to current filter parameters."

    total = len(df)
    country_dist = df["Country"].value_counts()
    top_country = country_dist.index[0] if not country_dist.empty else "N/A"
    top_country_launches = country_dist.iloc[0] if not country_dist.empty else 0
    top_country_share = (top_country_launches / total * 100) if total > 0 else 0

    comp_dist = df["Company_Name"].value_counts()
    top_comp = comp_dist.index[0] if not comp_dist.empty else "N/A"
    top_comp_launches = comp_dist.iloc[0] if not comp_dist.empty else 0

    russia_cnt = (df["Country"] == "Russia").sum()
    usa_cnt = (df["Country"] == "USA").sum()
    kazakh_cnt = (df["Country"] == "Kazakhstan").sum()
    china_cnt = (df["Country"] == "China").sum()
    india_cnt = (df["Country"] == "India").sum()

    cost_sub = df[df["Has_Cost_Data"]]
    median_cost = cost_sub["Launch_Cost"].median() if not cost_sub.empty else 0.0

    insights = (
        f"**🏛️ Historical Superpower Leadership:** In this filtered manifest of **{total:,}** missions, "
        f"**{top_country}** holds the lead with **{top_country_launches:,}** launches ({top_country_share:.1f}%). "
        f"Across space history, the USA (**{usa_cnt:,}**), Russia (**{russia_cnt:,}**), and Kazakhstan/Baikonur (**{kazakh_cnt:,}**) "
        f"dominate orbital history, with **{top_comp}** recording **{top_comp_launches:,}** flights.\n\n"
        f"**🚀 Emerging Asian Capabilities:** China has expanded rapidly to **{china_cnt:,}** flights, "
        f"while India's ISRO has conducted **{india_cnt:,}** orbital missions with world-class mission economics.\n\n"
        f"**💰 Transparent Financial Telemetry:** Of the filtered flights, **{len(cost_sub):,}** missions contain authentic reported budget figures, "
        f"yielding a historical median launch cost of **${median_cost:,.1f}M USD** across disclosed commercial and public space programs."
    )
    return insights

st.info(f"✨ **Automated Visual Intelligence & Historical Insights:**\n\n{generate_dynamic_insights(df_filtered)}")


# ==============================================================================
# 5 CORE INTERACTIVE DASHBOARD TABS
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 1. Mission Timeline",
    "🎯 2. Success Rate & Reliability",
    "💰 3. Launch Cost Analysis",
    "🗺️ 4. Global Launch Map",
    "🔍 5. Country Comparison & Search",
])

# ------------------------------------------------------------------------------
# TAB 1: MISSION TIMELINE
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("⏳ Chronological Mapping of Space Exploration (1957–2020)")
    st.caption("Objective 1: Historical Analysis — Trace launch cadence, decadal distribution, and major space eras.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig_decade = charts.build_decade_bar_chart(df_filtered)
        st.plotly_chart(fig_decade, use_container_width=True)

    with col_t2:
        fig_era = charts.build_era_distribution_chart(df_filtered)
        st.plotly_chart(fig_era, use_container_width=True)

    st.subheader("🌊 Annual Launch Trajectory")
    breakdown_opt = st.radio(
        "Decompose Annual Launches By:",
        options=["Country", "Company Name"],
        horizontal=True,
        key="timeline_breakdown_toggle",
    )
    fig_annual = charts.build_annual_timeline_chart(
        df_filtered,
        breakdown_by=breakdown_opt,
    )
    st.plotly_chart(fig_annual, use_container_width=True)

    with st.expander("📚 Historical Space Exploration Eras Guide"):
        st.markdown(
            """
            - **Space Race Era (1957–1975):** Sputnik, Vostok, Mercury, Gemini, and Apollo Moon landings. Characterized by superpower competition and foundational rocketry development.
            - **Space Shuttle & Mir Era (1976–1999):** Operational reusable Space Shuttle orbiters, Soviet/Russian Mir space station, deployment of the Hubble Space Telescope, and satellite commercialization.
            - **Commercialization & Asian Expansion (2000–2014):** International Space Station (ISS) continuous human operations, expansion of ISRO (India) and CNSA (China) launch infrastructure.
            - **Megaconstellations & Reusable Rockets (2015–2020):** Commercial vertical booster recovery, rapid rideshare cadence, and deployment of mega-constellations.
            """
        )

# ------------------------------------------------------------------------------
# TAB 2: SUCCESS RATE & RELIABILITY
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🎯 Mission Outcome Breakdown & Flight Reliability Benchmarks")
    st.caption("Objective 2: Reliability Analysis — Benchmark flight success rates across nations and decades.")

    col_s1, col_s2 = st.columns([1.1, 0.9])
    with col_s1:
        viz_choice = st.radio(
            "Hierarchical Visualization Mode:",
            options=["Sunburst Multi-Level Drilldown", "Treemap Proportional View"],
            horizontal=True,
            key="success_viz_choice",
        )
        if viz_choice == "Sunburst Multi-Level Drilldown":
            fig_hierarchy = charts.build_country_outcome_sunburst(df_filtered)
        else:
            fig_hierarchy = charts.build_country_outcome_treemap(df_filtered)
        st.plotly_chart(fig_hierarchy, use_container_width=True)

    with col_s2:
        fig_benchmark = charts.build_country_success_benchmark_chart(df_filtered, min_launches=15)
        st.plotly_chart(fig_benchmark, use_container_width=True)

    st.subheader("📈 Historical Flight Reliability Curve (1950s–2020s)")
    fig_reliability = charts.build_decadal_reliability_trend(df_filtered)
    st.plotly_chart(fig_reliability, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: LAUNCH COST ANALYSIS (AUTHENTIC DISCLOSED RECORDS)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("💰 Financial Telemetry & Launch Cost Intelligence")
    st.caption("Objective 3: Cost Analysis — Financial examination based strictly on authentic disclosed mission costs.")

    cost_df = df_filtered[df_filtered["Has_Cost_Data"]]

    if cost_df.empty:
        st.warning("No missions with disclosed cost data match the current filter selection.")
    else:
        avg_cost = cost_df["Launch_Cost"].mean()
        median_cost = cost_df["Launch_Cost"].median()
        max_cost = cost_df["Launch_Cost"].max()
        min_cost = cost_df["Launch_Cost"].min()

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.metric("Disclosed Cost Missions", f"{len(cost_df):,}", f"{(len(cost_df) / len(df_filtered) * 100):.1f}% of Active Filter")
        with col_c2:
            st.metric("Median Launch Cost", f"${median_cost:,.1f}M", help="Median reported cost per flight")
        with col_c3:
            st.metric("Mean Launch Cost", f"${avg_cost:,.1f}M", help="Average reported cost per flight")
        with col_c4:
            st.metric("Cost Range", f"${min_cost:,.1f}M – ${max_cost:,.0f}M", help="Min and Max disclosed costs")

        st.info(
            "ℹ️ **Authentic Data Transparency Note:** Historical mission cost figures are disclosed for a subset "
            f"of flights ({metadata['missions_with_cost']} in total dataset) representing commercial and post-Apollo government manifests. "
            "Soviet-era and early military flights did not publish cost figures. "
            "CosmosVis never imputes or invents fake budget data."
        )

        st.subheader("🔍 Reported Launch Cost vs Mission Year")
        fig_cost_scatter = charts.build_cost_vs_year_scatter(df_filtered)
        st.plotly_chart(fig_cost_scatter, use_container_width=True)

        col_cb1, col_cb2 = st.columns(2)
        with col_cb1:
            fig_top_cost = charts.build_top_expensive_missions_bar(df_filtered, top_n=10)
            st.plotly_chart(fig_top_cost, use_container_width=True)

        with col_cb2:
            fig_box_cost = charts.build_company_cost_distribution_box(df_filtered)
            st.plotly_chart(fig_box_cost, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: GLOBAL LAUNCH MAP & SPACEPORT INFRASTRUCTURE
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("🗺️ Global Spaceport Infrastructure & Launch Density")
    st.caption("Objective 4: Geospatial Mapping — Explore active orbital launch facilities with Geopy physics calculations.")

    mapped_count = metadata.get("mapped_sites_count", 0)
    unmapped_count = metadata.get("unmapped_sites_count", 0)

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.success(f"✅ **Geographically Mapped Facilities:** {mapped_count} active space centers & marine platforms with verified official WGS-84 coordinates.")
    with col_v2:
        if unmapped_count == 0:
            st.info("🎯 **Coordinate Integrity:** 100% of launch locations in uploaded dataset have verified geographic coordinates.")
        else:
            unmapped_list = ", ".join(metadata.get("unmapped_locations", []))
            st.warning(f"⚠️ **Unmapped Locations ({unmapped_count}):** {unmapped_list}")

    fig_map = charts.build_global_launch_map(df_filtered)
    st.plotly_chart(fig_map, use_container_width=True)

    col_m1, col_m2 = st.columns([1.1, 0.9])
    with col_m1:
        fig_rank = charts.build_site_volume_ranking_chart(df_filtered, top_n=12)
        st.plotly_chart(fig_rank, use_container_width=True)

    with col_m2:
        st.subheader("📏 Geopy Great-Circle Distance Calculator")
        st.caption("Compute ellipsoidal geodesic surface distances between any two global spaceports using Geopy (WGS-84).")

        site_list = sorted(df_full["Spaceport"].unique().tolist())
        col_sa, col_sb = st.columns(2)
        with col_sa:
            site_a = st.selectbox("Origin Spaceport A:", site_list, index=0, key="origin_site")
        with col_sb:
            default_b_idx = min(7, len(site_list) - 1)
            site_b = st.selectbox("Destination Spaceport B:", site_list, index=default_b_idx, key="dest_site")

        if site_a and site_b:
            pair_res = utils.compute_site_pair_distance(site_a, site_b, df_full)
            if pair_res:
                st.metric(
                    label=f"Geodesic Distance ({site_a} ➔ {site_b})",
                    value=f"{pair_res['distance_km']:,} km",
                    help="Ellipsoidal geodesic surface distance computed via Geopy using the WGS-84 standard ellipsoid.",
                )
                st.caption(
                    f"≈ {pair_res['distance_miles']:,} statute miles | {round(pair_res['distance_km'] / 1.852, 1):,} nautical miles"
                )

        st.subheader("🌍 Earth Rotation Velocity Assist")
        st.caption("Spaceports closer to the Equator receive higher tangential rotational assist velocity (v = 465.1 × cos(latitude) m/s), reducing propellant requirements.")

        equatorial_sites = (
            df_full[["Spaceport", "Country", "Latitude", "Equator_Dist_km", "Earth_Rotation_Boost_mps"]]
            .drop_duplicates(subset=["Spaceport"])
            .sort_values("Equator_Dist_km")
            .head(5)
        )
        st.dataframe(
            equatorial_sites.rename(columns={
                "Spaceport": "Spaceport Center",
                "Latitude": "Lat (°)",
                "Equator_Dist_km": "Dist to Equator (km)",
                "Earth_Rotation_Boost_mps": "Rotation Boost (m/s)"
            }),
            use_container_width=True,
            hide_index=True,
        )

# ------------------------------------------------------------------------------
# TAB 5: COUNTRY COMPARISON & LIVE MISSION SEARCH
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("🌐 Sovereign Country Comparison & Real-Time Mission Search")
    st.caption("Objective 5: Comparative Analysis — Compare any two spacefaring powers and search the authentic mission catalog.")

    st.markdown("#### ⚔️ Head-to-Head Country Comparison")
    all_nations = sorted(df_full["Country"].unique().tolist())

    col_ca, col_cb = st.columns(2)
    with col_ca:
        c1 = st.selectbox("Select Sovereign Nation 1:", all_nations, index=all_nations.index("USA") if "USA" in all_nations else 0, key="comp_c1")
    with col_cb:
        default_c2_idx = all_nations.index("Russia") if "Russia" in all_nations else min(1, len(all_nations) - 1)
        c2 = st.selectbox("Select Sovereign Nation 2:", all_nations, index=default_c2_idx, key="comp_c2")

    if c1 and c2:
        sub_c1 = df_full[df_full["Country"] == c1]
        sub_c2 = df_full[df_full["Country"] == c2]

        tot1, tot2 = len(sub_c1), len(sub_c2)
        sr1 = (sub_c1["Success_Binary"].mean() * 100) if tot1 > 0 else 0.0
        sr2 = (sub_c2["Success_Binary"].mean() * 100) if tot2 > 0 else 0.0
        comps1 = sub_c1["Company_Name"].nunique()
        comps2 = sub_c2["Company_Name"].nunique()

        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            st.metric(f"Total Launches ({c1} vs {c2})", f"{tot1:,} vs {tot2:,}", delta=f"{tot1 - tot2:+,} diff")
        with col_k2:
            st.metric(f"Success Rate ({c1} vs {c2})", f"{sr1:.1f}% vs {sr2:.1f}%", delta=f"{sr1 - sr2:+.1f}%")
        with col_k3:
            st.metric(f"Active Operators ({c1} vs {c2})", f"{comps1} vs {comps2}", delta=f"{comps1 - comps2:+d}")

        fig_compare = charts.build_country_comparison_bar(df_full, c1, c2)
        st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown("---")
    st.subheader("🔎 Interactive Mission Search Engine")
    st.caption("Search across rocket names, mission payloads, aerospace companies, and launch sites.")

    search_query = st.text_input(
        "Enter mission keyword, rocket model, or payload name (e.g. 'Falcon', 'Apollo', 'Soyuz', 'Chandrayaan', 'Hubble'):",
        placeholder="Type search terms here...",
    )

    if search_query:
        query_clean = search_query.strip().lower()
        search_mask = (
            df_full["Detail"].str.lower().str.contains(query_clean, na=False)
            | df_full["Rocket_Name"].str.lower().str.contains(query_clean, na=False)
            | df_full["Payload_Mission"].str.lower().str.contains(query_clean, na=False)
            | df_full["Company_Name"].str.lower().str.contains(query_clean, na=False)
            | df_full["Country"].str.lower().str.contains(query_clean, na=False)
            | df_full["Spaceport"].str.lower().str.contains(query_clean, na=False)
        )
        search_results = df_full[search_mask]
        st.markdown(f"**Found {len(search_results):,} matching missions for '{search_query}':**")
        st.dataframe(
            search_results[[
                "Year", "Company_Name", "Rocket_Name", "Payload_Mission",
                "Country", "Spaceport", "Mission_Status", "Launch_Cost"
            ]],
            use_container_width=True,
            height=300,
        )
    else:
        st.caption("Showing first 10 missions. Enter a keyword above to search the full historical catalog.")
        st.dataframe(
            df_full[[
                "Year", "Company_Name", "Rocket_Name", "Payload_Mission",
                "Country", "Spaceport", "Mission_Status", "Launch_Cost"
            ]].head(10),
            use_container_width=True,
        )


# ==============================================================================
# DATA EXPLORER & CSV EXPORT
# ==============================================================================
with st.expander("📥 Filtered Telemetry Data Explorer & CSV Export"):
    st.markdown(f"**Showing {len(df_filtered):,} matching records from active filters:**")
    st.dataframe(
        df_filtered[[
            "Year", "Company_Name", "Rocket_Name", "Payload_Mission",
            "Country", "Spaceport", "Rocket_Status", "Mission_Status",
            "Launch_Cost", "Latitude", "Longitude", "Equator_Dist_km", "Earth_Rotation_Boost_mps"
        ]],
        use_container_width=True,
        height=320,
    )

    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Telemetry (CSV)",
        data=csv_data,
        file_name="cosmosvis_filtered_space_missions.csv",
        mime="text/csv",
    )


# ==============================================================================
# PROFESSIONAL FOOTER (PURE STREAMLIT / MARKDOWN - ZERO HTML)
# ==============================================================================
st.markdown("---")
st.markdown(
    """
    **COSMOSVIS • GLOBAL ORBITAL INTELLIGENCE**

    CosmosVis is an academic M.Sc. Computer Science visual analytics project synthesizing
    historical orbital rocketry manifests, spaceport geographic coordinates, and flight reliability
    to provide interactive visual intelligence for aerospace researchers, students, and analysts.

    • **Core Technologies:** Python | Streamlit | Pandas | NumPy | Plotly | Geopy
    • **Data Ingestion:** Authentic Kaggle Manifests (1957–2020) • 100% Verified Telemetry • Zero Synthetic Data
    • **Geodesic Engine:** Geopy WGS-84 Ellipsoidal Modeling • 38 Global Spaceports Mapped

    *Dataset Source: Kaggle (All Space Missions from 1957) • NASA • Roscosmos • CNSA • ISRO • ESA • SpaceX*
    """
)
