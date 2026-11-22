"""
CosmosVis - Plotly Visualization Engine (charts.py)
Constructs high-performance interactive WebGL and SVG charts for all 5 dashboard sections:
1. Mission Timeline & Historical Eras
2. Hierarchical Success Rates & Reliability Benchmarks
3. Cost Efficiency & Financial Telemetry (Authentic Data)
4. Global Launch Map & Spaceport Heatmaps (Geopy-enriched)
5. Sovereign Nation Comparison & Fleet Breakdown

Built exclusively using Python, Plotly, Pandas, and NumPy.
Uses plain-text labels and tooltips with zero embedded HTML/CSS tags.
"""

from typing import Optional, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Typography & Color Palettes
FONT_FAMILY = "sans-serif"

PALETTE = [
    "#38BDF8",  # Sky Blue
    "#818CF8",  # Indigo
    "#C084FC",  # Violet
    "#F472B6",  # Pink
    "#34D399",  # Emerald Green
    "#FBBF24",  # Amber
    "#FB7185",  # Coral
    "#60A5FA",  # Light Blue
    "#A78BFA",  # Purple
    "#2DD4BF",  # Teal
]

STATUS_COLORS = {
    "Success": "#00E676",
    "Failure": "#FF5252",
    "Partial Failure": "#FFAB00",
    "Prelaunch Failure": "#D50000",
}


def hex_to_rgba(hex_color: str, alpha: float = 0.4) -> str:
    """Converts hex color string to rgba string with given alpha opacity."""
    hex_clean = hex_color.lstrip("#")
    if len(hex_clean) == 6:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    elif len(hex_clean) == 3:
        r = int(hex_clean[0] * 2, 16)
        g = int(hex_clean[1] * 2, 16)
        b = int(hex_clean[2] * 2, 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    return hex_color


def get_theme_colors(theme: str = "dark") -> dict:
    """Returns color definitions tailored to the active UI theme."""
    if theme == "light":
        return {
            "paper_bg": "#FFFFFF",
            "plot_bg": "#F8FAFC",
            "font_color": "#334155",
            "title_color": "#0F172A",
            "grid_color": "rgba(0, 0, 0, 0.08)",
            "line_color": "rgba(0, 0, 0, 0.15)",
            "legend_bg": "rgba(255, 255, 255, 0.95)",
            "legend_border": "rgba(0, 0, 0, 0.12)",
            "hover_bg": "#FFFFFF",
            "hover_border": "#0284C7",
            "hover_text": "#0F172A",
            "map_style": "carto-positron",
        }
    return {
        "paper_bg": "rgba(18, 24, 38, 0.92)",
        "plot_bg": "rgba(18, 24, 38, 0.92)",
        "font_color": "#CBD5E1",
        "title_color": "#E2E8F0",
        "grid_color": "rgba(255, 255, 255, 0.08)",
        "line_color": "rgba(255, 255, 255, 0.2)",
        "legend_bg": "rgba(15, 23, 42, 0.85)",
        "legend_border": "rgba(255, 255, 255, 0.15)",
        "hover_bg": "#0F172A",
        "hover_border": "#38BDF8",
        "hover_text": "#F8FAFC",
        "map_style": "carto-darkmatter",
    }


def apply_space_theme(fig: go.Figure, title: Optional[str] = None, theme: str = "dark") -> go.Figure:
    """Applies unified responsive aerospace telemetry styling across Plotly charts."""
    cfg = get_theme_colors(theme)
    fig.update_layout(
        title=dict(
            text=title if title else "",
            font=dict(family=FONT_FAMILY, size=15, color=cfg["title_color"]),
            x=0.02,
            y=0.96,
        ),
        paper_bgcolor=cfg["paper_bg"],
        plot_bgcolor=cfg["plot_bg"],
        font=dict(family=FONT_FAMILY, color=cfg["font_color"], size=12),
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            bgcolor=cfg["legend_bg"],
            bordercolor=cfg["legend_border"],
            borderwidth=1,
            font=dict(size=11, color=cfg["title_color"]),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(
            bgcolor=cfg["hover_bg"],
            bordercolor=cfg["hover_border"],
            font=dict(family=FONT_FAMILY, size=12, color=cfg["hover_text"]),
        ),
    )
    fig.update_xaxes(
        gridcolor=cfg["grid_color"],
        zerolinecolor=cfg["grid_color"],
        showline=True,
        linecolor=cfg["line_color"],
        tickfont=dict(color=cfg["font_color"], size=11, family=FONT_FAMILY),
    )
    fig.update_yaxes(
        gridcolor=cfg["grid_color"],
        zerolinecolor=cfg["grid_color"],
        showline=True,
        linecolor=cfg["line_color"],
        tickfont=dict(color=cfg["font_color"], size=11, family=FONT_FAMILY),
    )
    return fig


def create_empty_chart(message: str = "No data matching current filters", theme: str = "dark") -> go.Figure:
    """Fallback figure when active filters return 0 records."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(family=FONT_FAMILY, size=16, color="#94A3B8"),
    )
    return apply_space_theme(fig, theme=theme)


# ==============================================================================
# SECTION 1: MISSION TIMELINE CHARTS
# ==============================================================================

def build_decade_bar_chart(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Constructs 'Space Missions by Decade' bar chart highlighting mission volume
    and historical growth from 1950s to 2020s.
    """
    if df.empty:
        return create_empty_chart(theme=theme)

    decade_summary = (
        df.groupby(["Decade_Label", "Decade"])
        .size()
        .reset_index(name="Mission_Count")
        .sort_values("Decade")
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=decade_summary["Decade_Label"],
            y=decade_summary["Mission_Count"],
            text=decade_summary["Mission_Count"],
            textposition="outside",
            cliponaxis=False,
            marker=dict(
                color=decade_summary["Mission_Count"],
                colorscale=[
                    [0.0, "#38BDF8"],
                    [0.5, "#818CF8"],
                    [1.0, "#C084FC"],
                ],
                line=dict(color="rgba(255, 255, 255, 0.3)", width=1),
            ),
            hovertemplate="Decade: %{x}\nTotal Missions: %{y:,}",
        )
    )

    max_y = float(decade_summary["Mission_Count"].max()) if not decade_summary.empty else 100.0
    fig.update_layout(
        xaxis_title="Historical Decade",
        yaxis_title="Total Missions Launched",
        bargap=0.25,
        yaxis=dict(range=[0, max_y * 1.15]),
    )
    return apply_space_theme(fig, "Space Missions by Decade (1950s–2020s)", theme=theme)


def build_annual_timeline_chart(df: pd.DataFrame, breakdown_by: str = "Country", theme: str = "dark") -> go.Figure:
    """
    Chronological time-series chart showing annual launch frequency with stacked
    country or company composition across 1957–2020.
    """
    if df.empty:
        return create_empty_chart(theme=theme)

    group_col = "Country" if breakdown_by == "Country" else "Company_Name"
    top_cats = df[group_col].value_counts().nlargest(6).index.tolist()

    df_temp = df.copy()
    df_temp["Group_Category"] = df_temp[group_col].apply(
        lambda x: x if x in top_cats else "Other / International"
    )

    annual = (
        df_temp.groupby(["Year", "Group_Category"])
        .size()
        .reset_index(name="Launches")
        .sort_values("Year")
    )

    fig = px.area(
        annual,
        x="Year",
        y="Launches",
        color="Group_Category",
        color_discrete_sequence=PALETTE,
        hover_data={"Year": True, "Launches": True, "Group_Category": True},
    )

    # Set translucent fill opacity to 0.4 and crisp boundary line width
    for idx, trace in enumerate(fig.data):
        trace_color = PALETTE[idx % len(PALETTE)]
        trace.line = dict(width=2, color=trace_color)
        trace.fillcolor = hex_to_rgba(trace_color, 0.4)

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Annual Orbital Launches",
        hovermode="x unified",
    )
    return apply_space_theme(fig, f"Annual Orbital Launch Trajectory (Grouped by {breakdown_by})", theme=theme)


def build_era_distribution_chart(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Distribution of launches across the 4 major space exploration eras.
    Vertical bar chart with clean plain-text labels and colored by success rate.
    Uses concise category labels to prevent clipping/overlapping, while preserving
    the full historical era names in hover telemetry.
    """
    if df.empty:
        return create_empty_chart(theme=theme)

    def map_era_info(era_str: str):
        if "Space Race" in era_str:
            return 0, "Space Race (1957-1975)", "Space Race Era (1957-1975)"
        elif "Shuttle" in era_str or "Mir" in era_str:
            return 1, "Shuttle & Mir (1976-1999)", "Space Shuttle & Mir Era (1976-1999)"
        elif "Commercial" in era_str or "Asian" in era_str:
            return 2, "Commercial Era (2000-2014)", "Commercial & Asian Expansion (2000-2014)"
        elif "Megaconstellation" in era_str or "Reusable" in era_str:
            return 3, "Megaconstellations (2015-2020)", "Megaconstellations & Reusable Rockets (2015-2020)"
        return 99, era_str, era_str

    era_summary = (
        df.groupby("Era")
        .agg(
            Total=("Detail", "count"),
            Successes=("Success_Binary", "sum"),
        )
        .reset_index()
    )

    era_summary["Success_Rate"] = (
        (era_summary["Successes"] / era_summary["Total"]) * 100.0
    ).clip(lower=0.0, upper=100.0).round(1)

    mapped_info = [map_era_info(e) for e in era_summary["Era"]]
    era_summary["Order"] = [m[0] for m in mapped_info]
    era_summary["Era_Display"] = [m[1] for m in mapped_info]
    era_summary["Full_Era_Name"] = [m[2] for m in mapped_info]

    # Sort chronologically left-to-right
    era_summary = era_summary.sort_values("Order", ascending=True).reset_index(drop=True)

    min_rate = max(0.0, float(era_summary["Success_Rate"].min()) - 4.0)
    max_y = float(era_summary["Total"].max()) if not era_summary.empty else 100.0

    cfg = get_theme_colors(theme)

    # Sleek, compact colorbar on the right with comfortable margin
    colorbar_config = dict(
        title=dict(text="Success %", font=dict(color=cfg["title_color"], size=11)),
        tickfont=dict(color=cfg["font_color"], size=10),
        ticksuffix="%",
        x=1.02,
        xanchor="left",
        len=0.75,
        y=0.5,
        thickness=14,
        bgcolor=cfg["legend_bg"],
        bordercolor=cfg["legend_border"],
        borderwidth=1,
    )

    marker_config = dict(
        color=era_summary["Success_Rate"],
        colorscale="Tealgrn",
        cmin=min_rate,
        cmax=100.0,
        colorbar=colorbar_config,
        line=dict(color=cfg["line_color"], width=1),
    )

    customdata = np.stack([era_summary["Full_Era_Name"], era_summary["Success_Rate"]], axis=-1)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=era_summary["Era_Display"],
            y=era_summary["Total"],
            texttemplate="%{y:,}",
            textposition="outside",
            cliponaxis=False,
            textfont=dict(
                color=cfg["title_color"],
                size=11,
                family=FONT_FAMILY,
            ),
            marker=marker_config,
            customdata=customdata,
            hovertemplate=(
                "Era: %{customdata[0]}\n"
                "Total Missions: %{y:,}\n"
                "Success Rate: %{customdata[1]:.1f}%"
            ),
        )
    )

    fig.update_xaxes(
        title="",
        tickangle=-25,
        tickfont=dict(color=cfg["title_color"], size=10, family=FONT_FAMILY),
        showgrid=False,
        automargin=True,
        range=[-0.6, 3.6],
    )
    fig.update_yaxes(
        title="Total Missions",
        range=[0, max_y * 1.18],
        gridcolor=cfg["grid_color"],
        tickfont=dict(color=cfg["font_color"], size=11, family=FONT_FAMILY),
        automargin=True,
    )
    fig.update_layout(
        template="none",
        height=450,
        bargap=0.35,
        paper_bgcolor=cfg["paper_bg"],
        plot_bgcolor=cfg["plot_bg"],
        font=dict(family=FONT_FAMILY, color=cfg["font_color"], size=12),
        margin=dict(l=60, r=80, t=55, b=85),
        title=dict(
            text="Mission Distribution Across Historical Eras",
            font=dict(family=FONT_FAMILY, size=15, color=cfg["title_color"]),
            x=0.02,
            y=0.96,
        ),
    )
    return fig


# ==============================================================================
# SECTION 2: SUCCESS RATE & RELIABILITY CHARTS
# ==============================================================================

def build_country_outcome_sunburst(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Constructs hierarchical Sunburst chart: Country -> Mission Status outcome.
    Groups all countries except the top 5 into 'Others' to eliminate visual clutter.
    """
    if df.empty:
        return create_empty_chart(theme=theme)

    top_5_countries = df["Country"].value_counts().nlargest(5).index.tolist()

    df_sun = df.copy()
    df_sun["Country_Grouped"] = df_sun["Country"].apply(
        lambda c: c if c in top_5_countries else "Others"
    )

    grouped = (
        df_sun.groupby(["Country_Grouped", "Mission_Status"])
        .size()
        .reset_index(name="Count")
    )

    fig = px.sunburst(
        grouped,
        path=["Country_Grouped", "Mission_Status"],
        values="Count",
        color="Mission_Status",
        color_discrete_map=STATUS_COLORS,
        hover_data={"Count": True},
    )

    cfg = get_theme_colors(theme)
    fig.update_traces(
        textinfo="label+percent entry",
        insidetextorientation="radial",
        marker=dict(line=dict(color=cfg["paper_bg"], width=1.5)),
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return apply_space_theme(fig, "Hierarchical Outcomes: Top 5 Nations + Others", theme=theme)


def build_country_outcome_treemap(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Treemap visualization of outcomes cleanly grouped to top 5 nations + Others."""
    if df.empty:
        return create_empty_chart(theme=theme)

    top_5_countries = df["Country"].value_counts().nlargest(5).index.tolist()
    df_tree = df.copy()
    df_tree["Country_Grouped"] = df_tree["Country"].apply(
        lambda c: c if c in top_5_countries else "Others"
    )

    grouped = (
        df_tree.groupby(["Country_Grouped", "Mission_Status"])
        .size()
        .reset_index(name="Missions")
    )

    fig = px.treemap(
        grouped,
        path=["Country_Grouped", "Mission_Status"],
        values="Missions",
        color="Mission_Status",
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_traces(marker=dict(cornerradius=4))
    return apply_space_theme(fig, "Treemap: Top 5 Space Powers + Others", theme=theme)


def build_country_success_benchmark_chart(df: pd.DataFrame, min_launches: int = 15, theme: str = "dark") -> go.Figure:
    """
    Benchmark horizontal bar chart of mission success rates across spacefaring nations,
    annotating total missions count for statistical context.
    """
    if df.empty:
        return create_empty_chart(theme=theme)

    summary = (
        df.groupby("Country")
        .agg(
            Total=("Detail", "count"),
            Successes=("Success_Binary", "sum"),
        )
        .reset_index()
    )
    summary = summary[summary["Total"] >= min_launches].copy()
    if summary.empty:
        summary = (
            df.groupby("Country")
            .agg(Total=("Detail", "count"), Successes=("Success_Binary", "sum"))
            .reset_index()
        )

    summary["Success_Rate"] = round((summary["Successes"] / summary["Total"]) * 100, 2)
    summary = summary.sort_values("Success_Rate", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=summary["Country"],
            x=summary["Success_Rate"],
            orientation="h",
            text=[f"{rate:.1f}% ({tot:,} launches)" for rate, tot in zip(summary["Success_Rate"], summary["Total"])],
            textposition="inside",
            marker=dict(
                color=summary["Success_Rate"],
                colorscale="Viridis",
                line=dict(color="rgba(255, 255, 255, 0.2)", width=1),
            ),
            hovertemplate="%{y}\nSuccess Rate: %{x:.2f}%",
        )
    )

    fig.update_layout(
        xaxis_title="Success Rate (%)",
        yaxis_title="",
        xaxis=dict(range=[0, 105]),
    )
    return apply_space_theme(fig, f"National Reliability Benchmark (Min. {min_launches} Launches)", theme=theme)


def build_decadal_reliability_trend(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Plots the historical reliability curve over the decades."""
    if df.empty:
        return create_empty_chart(theme=theme)

    decadal = (
        df.groupby(["Decade", "Decade_Label"])
        .agg(
            Total=("Detail", "count"),
            Success_Rate=("Success_Binary", lambda s: round(s.mean() * 100, 2)),
        )
        .reset_index()
        .sort_values("Decade")
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=decadal["Decade_Label"],
            y=decadal["Success_Rate"],
            mode="lines+markers",
            name="Success Rate %",
            line=dict(color="#00F2FE", width=3),
            marker=dict(size=9, color="#FFFFFF", line=dict(color="#00F2FE", width=2)),
            hovertemplate="%{x}\nSuccess Rate: %{y:.2f}%",
        )
    )

    fig.update_layout(
        xaxis_title="Decade",
        yaxis_title="Success Rate (%)",
        yaxis=dict(range=[50, 102]),
    )
    return apply_space_theme(fig, "Historical Evolution of Spaceflight Reliability (1950s–2020s)", theme=theme)


# ==============================================================================
# SECTION 3: COST ANALYSIS CHARTS (AUTHENTIC REPORTED COSTS ONLY)
# ==============================================================================

def build_cost_vs_year_scatter(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Constructs Launch Cost ($M) vs Launch Year scatter plot with NumPy-calculated
    linear regression trendline, plotted exclusively for real disclosed costs.
    Zero external dependencies (no statsmodels).
    """
    cost_df = df[df["Has_Cost_Data"]].copy()
    if cost_df.empty:
        return create_empty_chart("No cost data available for active filters", theme=theme)

    fig = px.scatter(
        cost_df,
        x="Launch_Cost",
        y="Year",
        color="Rocket_Status",
        color_discrete_map={"Active": "#00FFB2", "Retired": "#FF7043"},
        hover_name="Detail",
        hover_data={
            "Launch_Cost": ":$.1fM",
            "Company_Name": True,
            "Country": True,
            "Rocket_Status": True,
            "Mission_Status": True,
            "Year": True,
        },
    )

    for trace in fig.data:
        if trace.mode == "markers" or "markers" in (trace.mode or ""):
            trace.marker.size = 6
            trace.marker.opacity = 0.65
            trace.marker.line = dict(width=0.5, color="rgba(255, 255, 255, 0.4)")

    # Pure NumPy linear regression trendline (satisfies six-technology constraint)
    valid_pts = cost_df[["Launch_Cost", "Year"]].dropna()
    if len(valid_pts) >= 2 and valid_pts["Launch_Cost"].nunique() > 1:
        x_vals = valid_pts["Launch_Cost"].values
        y_vals = valid_pts["Year"].values
        poly_coeff = np.polyfit(x_vals, y_vals, 1)
        x_trend = np.linspace(x_vals.min(), x_vals.max(), 50)
        y_trend = np.polyval(poly_coeff, x_trend)
        fig.add_trace(
            go.Scatter(
                x=x_trend,
                y=y_trend,
                mode="lines",
                name="Trendline (OLS)",
                line=dict(color="#38BDF8", width=2.5, dash="dash"),
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        xaxis_title="Reported Launch Cost ($ Millions USD)",
        yaxis_title="Mission Year",
        legend_title="Rocket Status",
    )
    return apply_space_theme(fig, f"Reported Launch Cost vs Year ({len(cost_df):,} Missions With Disclosed Costs)", theme=theme)


def build_top_expensive_missions_bar(df: pd.DataFrame, top_n: int = 10, theme: str = "dark") -> go.Figure:
    """Bar chart of the highest reported launch costs in space history."""
    cost_df = df[df["Has_Cost_Data"]].copy()
    if cost_df.empty:
        return create_empty_chart("No cost data available for active filters", theme=theme)

    top_costs = (
        cost_df.sort_values("Launch_Cost", ascending=False)
        .drop_duplicates(subset=["Rocket_Name", "Company_Name"])
        .head(top_n)
        .sort_values("Launch_Cost", ascending=True)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=top_costs["Rocket_Name"] + " (" + top_costs["Company_Name"] + ")",
            x=top_costs["Launch_Cost"],
            orientation="h",
            text=[f"${c:,.1f}M" for c in top_costs["Launch_Cost"]],
            textposition="outside",
            cliponaxis=False,
            marker=dict(
                color=top_costs["Launch_Cost"],
                colorscale="Plasma",
                line=dict(color="rgba(255, 255, 255, 0.2)", width=1),
            ),
            hovertemplate="%{y}\nCost: $%{x:,.1f}M USD",
        )
    )

    max_c = float(top_costs["Launch_Cost"].max()) if not top_costs.empty else 100.0
    fig.update_layout(
        xaxis_title="Launch Cost ($ Millions USD)",
        yaxis_title="",
        xaxis=dict(range=[0, max_c * 1.2]),
    )
    return apply_space_theme(fig, f"Top {top_n} Most Capital-Intensive Launch Systems", theme=theme)


def build_company_cost_distribution_box(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Boxplot of launch costs across major aerospace companies."""
    cost_df = df[df["Has_Cost_Data"]].copy()
    if cost_df.empty:
        return create_empty_chart("No cost data available for active filters", theme=theme)

    # Filter companies with >= 5 costed launches
    comp_counts = cost_df["Company_Name"].value_counts()
    top_comps = comp_counts[comp_counts >= 5].index.tolist()
    if not top_comps:
        top_comps = comp_counts.head(5).index.tolist()

    sub = cost_df[cost_df["Company_Name"].isin(top_comps)].copy()

    fig = px.box(
        sub,
        x="Company_Name",
        y="Launch_Cost",
        color="Company_Name",
        color_discrete_sequence=PALETTE,
        points="all",
        hover_data=["Detail", "Year", "Mission_Status"],
    )

    fig.update_layout(
        xaxis_title="Aerospace Operator",
        yaxis_title="Launch Cost ($ Millions USD)",
        showlegend=False,
    )
    return apply_space_theme(fig, "Cost Distribution Across Major Operators ($M USD)", theme=theme)


# ==============================================================================
# SECTION 4: GLOBAL LAUNCH MAP & SPACEPORT INFRASTRUCTURE
# ==============================================================================

def build_global_launch_map(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Constructs high-visibility interactive world map of spaceports.
    Uses 'carto-darkmatter' in dark mode and 'carto-positron' in light mode.
    Prominent marker sizes scale cleanly with launch volume.
    Excludes any launch sites without verified geographic coordinates.
    """
    if df.empty:
        return create_empty_chart(theme=theme)

    # Filter strictly to valid, reliably mapped coordinates
    geo_df = df[df["Latitude"].notna() & df["Longitude"].notna()].copy()
    if geo_df.empty:
        return create_empty_chart("No verified geographic coordinates available for active filter", theme=theme)

    site_summary = (
        geo_df.groupby(["Spaceport", "Country", "Latitude", "Longitude"])
        .agg(
            Total_Launches=("Detail", "count"),
            Success_Count=("Success_Binary", "sum"),
            Equator_Dist_km=("Equator_Dist_km", "first"),
            Rotation_Boost_mps=("Earth_Rotation_Boost_mps", "first"),
            Facility_Type=("Facility_Type", "first"),
        )
        .reset_index()
    )

    site_summary["Success_Rate"] = round(
        (site_summary["Success_Count"] / site_summary["Total_Launches"]) * 100, 1
    )

    # Scaled marker sizes
    site_summary["Marker_Size"] = np.sqrt(site_summary["Total_Launches"]) * 3.5 + 10

    cfg = get_theme_colors(theme)
    map_func = getattr(px, "scatter_map", None)
    style_param = "map_style"
    if map_func is None:
        map_func = getattr(px, "scatter_mapbox")
        style_param = "mapbox_style"

    kwargs = {
        "lat": "Latitude",
        "lon": "Longitude",
        "size": "Marker_Size",
        "color": "Success_Rate",
        "color_continuous_scale": "Turbo",
        "range_color": [70, 100],
        style_param: cfg["map_style"],
        "zoom": 1.1,
        "center": dict(lat=22.0, lon=15.0),
        "size_max": 40,
    }

    fig = map_func(site_summary, **kwargs)

    customdata = site_summary[[
        "Spaceport", "Country", "Total_Launches", "Success_Rate",
        "Latitude", "Longitude", "Equator_Dist_km", "Rotation_Boost_mps", "Facility_Type"
    ]].values

    fig.update_traces(
        customdata=customdata,
        marker=dict(opacity=0.9),
        hovertemplate=(
            "%{customdata[0]}\n"
            "Country: %{customdata[1]}\n"
            "Facility Type: %{customdata[8]}\n"
            "Total Launches: %{customdata[2]:,}\n"
            "Success Rate: %{customdata[3]:.1f}%\n"
            "Coordinates: %{customdata[4]:.4f}°, %{customdata[5]:.4f}°\n"
            "Distance to Equator: %{customdata[6]:,.0f} km\n"
            "Earth Rotation Assist: %{customdata[7]:.1f} m/s"
        ),
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=35, b=0),
        height=580,
        coloraxis_colorbar=dict(
            title=dict(text="Success %", font=dict(color=cfg["title_color"])),
            tickfont=dict(color=cfg["font_color"]),
            bgcolor=cfg["legend_bg"],
            bordercolor=cfg["legend_border"],
            borderwidth=1,
            len=0.75,
            x=0.98,
        ),
    )

    return apply_space_theme(fig, f"Global Spaceport Infrastructure & Launch Density ({len(site_summary)} Active Centers)", theme=theme)


def build_site_volume_ranking_chart(df: pd.DataFrame, top_n: int = 12, theme: str = "dark") -> go.Figure:
    """Ranks spaceports by cumulative missions launched."""
    if df.empty:
        return create_empty_chart(theme=theme)

    site_counts = (
        df.groupby(["Spaceport", "Country"])
        .size()
        .reset_index(name="Missions")
        .sort_values("Missions", ascending=True)
        .tail(top_n)
    )

    cfg = get_theme_colors(theme)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=site_counts["Spaceport"],
            x=site_counts["Missions"],
            orientation="h",
            text=site_counts["Missions"],
            textposition="outside",
            cliponaxis=False,
            marker=dict(
                color=site_counts["Missions"],
                colorscale="Blues",
                line=dict(color=cfg["line_color"], width=1),
            ),
            hovertemplate="%{y}\nLaunches: %{x:,}",
        )
    )

    max_x = float(site_counts["Missions"].max()) if not site_counts.empty else 100.0
    fig.update_layout(
        xaxis_title="Cumulative Orbital Launches",
        yaxis_title="",
        xaxis=dict(range=[0, max_x * 1.18]),
    )
    return apply_space_theme(fig, f"Top {top_n} Most Active Spaceports Globally", theme=theme)


# ==============================================================================
# SECTION 5: SOVEREIGN NATION COMPARISON CHARTS
# ==============================================================================

def build_country_comparison_bar(df: pd.DataFrame, country_a: str, country_b: str, theme: str = "dark") -> go.Figure:
    """
    Constructs a side-by-side grouped bar chart comparing launches per decade
    between two chosen spacefaring nations.
    """
    sub = df[df["Country"].isin([country_a, country_b])].copy()
    if sub.empty:
        return create_empty_chart(f"No launches found for {country_a} or {country_b}", theme=theme)

    decade_counts = (
        sub.groupby(["Decade_Label", "Decade", "Country"])
        .size()
        .reset_index(name="Launches")
        .sort_values("Decade")
    )

    colors = {country_a: "#38BDF8", country_b: "#F472B6"}

    fig = px.bar(
        decade_counts,
        x="Decade_Label",
        y="Launches",
        color="Country",
        barmode="group",
        color_discrete_map=colors,
        text="Launches",
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        xaxis_title="Decade",
        yaxis_title="Missions Launched",
        legend_title="Country",
    )
    return apply_space_theme(fig, f"Decadal Launch Comparison: {country_a} vs {country_b}", theme=theme)
