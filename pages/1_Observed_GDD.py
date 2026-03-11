"""Page 1 — Observed GDD (SILO historical data only)."""

import os
import sys
from datetime import timedelta

import folium
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    FOOTER_HTML,
    LOCATIONS,
    LOCATION_NAMES,
    PAGE_CSS,
    calc_gdd,
    fetch_silo,
    info_box,
    metric_card,
    today_brisbane,
    validate_email,
    warn_box,
)

st.set_page_config(
    page_title="Observed GDD | Agronomy Tools",
    layout="wide",
)
st.markdown(PAGE_CSS, unsafe_allow_html=True)

st.title("Observed GDD")
st.markdown(
    "Accumulated Growing Degree Days from planting using historical SILO weather observations."
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")

    loc_name = st.selectbox("Location", LOCATION_NAMES, key="obs_loc")
    if loc_name == "Custom":
        lat = st.number_input("Latitude", value=-27.9488, format="%.4f", key="obs_lat_c")
        lon = st.number_input("Longitude", value=152.5790, format="%.4f", key="obs_lon_c")
    else:
        lat = LOCATIONS[loc_name]["lat"]
        lon = LOCATIONS[loc_name]["lon"]
        st.caption(f"Lat: {lat}  |  Lon: {lon}")

    # Interactive map — ESRI World Imagery (satellite)
    m = folium.Map(
        location=[lat, lon],
        zoom_start=13,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
    )
    folium.Marker(
        [lat, lon],
        popup=f"<b>{loc_name}</b><br>{lat:.4f}, {lon:.4f}",
        tooltip=loc_name,
        icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
    ).add_to(m)
    st_folium(m, height=220, use_container_width=True, returned_objects=[])

    st.divider()

    today = today_brisbane()
    yesterday = today - timedelta(days=1)

    planting_date = st.date_input(
        "Planting date",
        value=None,
        max_value=yesterday,
        format="YYYY/MM/DD",
        key="obs_plant",
    )
    end_date = st.date_input(
        "End date",
        value=None,
        min_value=planting_date,
        max_value=yesterday,
        format="YYYY/MM/DD",
        help="Defaults to yesterday — the last day SILO observed data is available.",
        key="obs_end",
    )

    st.divider()

    email = st.text_input(
        "SILO email address",
        value="silodata@proton.me",
        key="obs_email",
    )

    st.divider()

    tbase = st.number_input(
        "Tbase (°C)",
        value=10.0,
        min_value=-10.0,
        max_value=30.0,
        step=0.5,
        key="obs_tbase",
    )
    tmax_cap = st.number_input(
        "Tmax cap (°C)",
        value=33.0,
        min_value=20.0,
        max_value=60.0,
        step=0.5,
        key="obs_tmax",
    )

    st.divider()

    heat_stress_on = st.checkbox("Count heat stress days", value=False, key="obs_hs_on")
    heat_stress_temp = st.number_input(
        "Heat stress threshold (°C)",
        value=35.0,
        min_value=20.0,
        max_value=55.0,
        step=0.5,
        key="obs_hs_temp",
        disabled=not heat_stress_on,
        help="Count days where Tmax exceeds this temperature.",
    )

    run = st.button("Calculate GDD", type="primary", use_container_width=True)

    st.divider()
    st.caption(
        "SILO observed data is available up to yesterday (Brisbane time). "
        "A valid email is required for SILO DataDrill access."
    )

# ── Guard ─────────────────────────────────────────────────────────────────────
if not run:
    st.markdown(
        info_box("Configure settings in the sidebar and click <strong>Calculate GDD</strong> to begin."),
        unsafe_allow_html=True,
    )
    st.stop()

# ── Validation ────────────────────────────────────────────────────────────────
errors: list[str] = []
if not validate_email(email):
    errors.append("Please enter a valid email address for the SILO request.")
if planting_date is None:
    errors.append("Please select a planting date.")
if end_date is None:
    errors.append("Please select an end date.")
if planting_date and end_date and planting_date > end_date:
    errors.append("Planting date must be on or before the end date.")

if errors:
    for e in errors:
        st.error(e)
    st.stop()

# ── Fetch SILO ────────────────────────────────────────────────────────────────
with st.spinner("Fetching SILO observed data..."):
    try:
        wx = fetch_silo(
            lat,
            lon,
            email,
            planting_date.strftime("%Y%m%d"),
            end_date.strftime("%Y%m%d"),
        )
    except Exception as exc:
        st.error(f"SILO request failed: {exc}")
        st.stop()

if wx.empty:
    st.error("SILO returned no data for the specified date range and location.")
    st.stop()

# ── Compute GDD ───────────────────────────────────────────────────────────────
wx = wx.copy()
wx["tmax_eff"] = np.minimum(wx["maxt"], tmax_cap)
wx["gdd"] = calc_gdd(wx["mint"].values, wx["maxt"].values, tbase, tmax_cap)
wx["cumulative_gdd"] = wx["gdd"].cumsum()

obs_last_day = wx["date"].max()
total_gdd = float(wx["gdd"].sum())
calendar_days = (obs_last_day - planting_date).days + 1
avg_daily = total_gdd / max(len(wx), 1)

# ── Heat stress ───────────────────────────────────────────────────────────────
heat_stress_days = int((wx["maxt"] > heat_stress_temp).sum()) if heat_stress_on else None

# ── Metrics ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-h">Summary</div>', unsafe_allow_html=True)

cols = st.columns(4 if heat_stress_on else 3)
with cols[0]:
    st.markdown(
        metric_card("Total GDD", f"{total_gdd:.1f}", f"°C-days · Tbase {tbase}°C · cap {tmax_cap}°C"),
        unsafe_allow_html=True,
    )
with cols[1]:
    st.markdown(
        metric_card("Calendar Days", str(calendar_days), f"{planting_date} to {obs_last_day}"),
        unsafe_allow_html=True,
    )
with cols[2]:
    st.markdown(
        metric_card("Avg GDD / Day", f"{avg_daily:.1f}", f"°C-days · last obs: {obs_last_day}"),
        unsafe_allow_html=True,
    )
if heat_stress_on:
    with cols[3]:
        st.markdown(
            metric_card(
                "Heat Stress Days",
                str(heat_stress_days),
                f"days with Tmax > {heat_stress_temp}°C",
            ),
            unsafe_allow_html=True,
        )

# ── Cumulative GDD chart ──────────────────────────────────────────────────────
st.markdown('<div class="section-h">Cumulative GDD Over Time</div>', unsafe_allow_html=True)

x_dates = [str(d) for d in wx["date"]]

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=x_dates,
        y=wx["cumulative_gdd"].round(1),
        name="Cumulative GDD",
        mode="lines",
        line=dict(color="#2e7d32", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(46,125,50,0.10)",
        hovertemplate="<b>%{x}</b><br>Cumulative GDD: %{y:.1f} °C-days<extra></extra>",
    )
)
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Cumulative GDD (°C-days)",
    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=10, b=0),
    height=380,
)
fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
st.plotly_chart(fig, use_container_width=True)

# ── Daily GDD bar chart ───────────────────────────────────────────────────────
with st.expander("Daily GDD bar chart"):
    fig2 = go.Figure(
        go.Bar(
            x=x_dates,
            y=wx["gdd"].round(1),
            marker_color="#4caf50",
            name="Daily GDD",
            hovertemplate="<b>%{x}</b><br>Daily GDD: %{y:.1f} °C-days<extra></extra>",
        )
    )
    fig2.update_layout(
        xaxis_title="Date",
        yaxis_title="Daily GDD (°C-days)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
    )
    fig2.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    fig2.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    st.plotly_chart(fig2, use_container_width=True)

# ── Data table ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-h">Observed Data (SILO)</div>', unsafe_allow_html=True)

display_df = (
    wx[["date", "mint", "maxt", "tmax_eff", "gdd", "cumulative_gdd"]]
    .copy()
    .rename(columns={
        "date": "Date",
        "mint": "Min Temp (°C)",
        "maxt": "Max Temp (°C)",
        "tmax_eff": "Tmax Eff (°C)",
        "gdd": "GDD (°C-days)",
        "cumulative_gdd": "Cumulative GDD",
    })
)
for col in ["Min Temp (°C)", "Max Temp (°C)", "Tmax Eff (°C)", "GDD (°C-days)", "Cumulative GDD"]:
    display_df[col] = display_df[col].round(1)
display_df["Date"] = display_df["Date"].astype(str)


def style_tmax(df):
    if heat_stress_on:
        return df.style.map(
            lambda v: "background-color: #ffcccc;" if v > heat_stress_temp else "",
            subset=["Max Temp (°C)"],
        )
    return df.style


st.markdown(f"**Last 20 days** of {len(display_df)} total days observed:")
st.dataframe(style_tmax(display_df.tail(20)), use_container_width=True, hide_index=True)

with st.expander(f"Show all {len(display_df)} days"):
    st.dataframe(style_tmax(display_df), use_container_width=True, hide_index=True)

st.markdown(FOOTER_HTML, unsafe_allow_html=True)
