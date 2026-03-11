"""Page 2 — Observed + Forecasted GDD (SILO historical + Open-Meteo 16-day forecast)."""

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
    fetch_openmeteo,
    fetch_silo,
    info_box,
    metric_card,
    today_brisbane,
    validate_email,
    warn_box,
)

st.set_page_config(
    page_title="Observed + Forecasted GDD | Agronomy Tools",
    layout="wide",
)
st.markdown(PAGE_CSS, unsafe_allow_html=True)

st.title("Observed + Forecasted GDD")
st.markdown(
    "SILO observed data (up to yesterday) combined with Open-Meteo 16-day forecast "
    "to project GDD from planting through to harvest."
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")

    loc_name = st.selectbox("Location", LOCATION_NAMES, key="fc_loc")
    if loc_name == "Custom":
        lat = st.number_input("Latitude", value=-27.9488, format="%.4f", key="fc_lat_c")
        lon = st.number_input("Longitude", value=152.5790, format="%.4f", key="fc_lon_c")
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
        format="YYYY/MM/DD",
        key="fc_plant",
    )
    preh_date = st.date_input(
        "Pre-harvest date",
        value=None,
        format="YYYY/MM/DD",
        key="fc_preh",
    )
    harv_date = st.date_input(
        "Harvest date",
        value=None,
        format="YYYY/MM/DD",
        key="fc_harv",
    )

    st.divider()

    email = st.text_input(
        "SILO email address",
        value="silodata@proton.me",
        key="fc_email",
    )

    st.divider()

    tbase = st.number_input(
        "Tbase (°C)",
        value=10.0,
        min_value=-10.0,
        max_value=30.0,
        step=0.5,
        key="fc_tbase",
    )
    tmax_cap = st.number_input(
        "Tmax cap (°C)",
        value=33.0,
        min_value=20.0,
        max_value=60.0,
        step=0.5,
        key="fc_tmax",
    )

    st.divider()

    heat_stress_on = st.checkbox("Count heat stress days", value=False, key="fc_hs_on")
    heat_stress_temp = st.number_input(
        "Heat stress threshold (°C)",
        value=35.0,
        min_value=20.0,
        max_value=55.0,
        step=0.5,
        key="fc_hs_temp",
        disabled=not heat_stress_on,
        help="Count days where Tmax exceeds this temperature.",
    )

    run = st.button("Calculate GDD", type="primary", use_container_width=True)

    st.divider()
    st.caption(
        "SILO observed data is available up to yesterday (Brisbane time). "
        "Open-Meteo forecast is typically available for ~16 days from today."
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
if harv_date is None:
    errors.append("Please select a harvest date.")
if planting_date and preh_date and preh_date < planting_date:
    errors.append("Pre-harvest date cannot be before planting date.")
if preh_date and harv_date and harv_date < preh_date:
    errors.append("Harvest date cannot be before pre-harvest date.")

if errors:
    for e in errors:
        st.error(e)
    st.stop()

# ── Fetch SILO ────────────────────────────────────────────────────────────────
obs_end = yesterday

with st.spinner("Fetching SILO observed data..."):
    try:
        wx = fetch_silo(
            lat,
            lon,
            email,
            planting_date.strftime("%Y%m%d"),
            obs_end.strftime("%Y%m%d"),
        )
    except Exception as exc:
        st.error(f"SILO request failed: {exc}")
        st.stop()

if wx.empty:
    st.error("SILO returned no data for the specified date range and location.")
    st.stop()

# ── Compute observed GDD ──────────────────────────────────────────────────────
wx = wx.copy()
wx["tmax_eff"] = np.minimum(wx["maxt"], tmax_cap)
wx["gdd"] = calc_gdd(wx["mint"].values, wx["maxt"].values, tbase, tmax_cap)

obs_last_day = wx["date"].max()

obs_end_for_harv = min(obs_last_day, harv_date)
mask_obs_all = (wx["date"] >= planting_date) & (wx["date"] <= obs_end_for_harv)
obs_plant_to_harv = float(wx.loc[mask_obs_all, "gdd"].sum())

if preh_date:
    obs_end_for_preh = min(preh_date, obs_last_day)
    mask_p2preh = (wx["date"] >= planting_date) & (wx["date"] <= obs_end_for_preh)
    obs_plant_to_preh = float(wx.loc[mask_p2preh, "gdd"].sum())

    obs_preh_to_lastobs = 0.0
    if obs_end_for_harv >= preh_date:
        mask_preh2harv = (wx["date"] >= preh_date) & (wx["date"] <= obs_end_for_harv)
        obs_preh_to_lastobs = float(wx.loc[mask_preh2harv, "gdd"].sum())

# ── Fetch Open-Meteo forecast ─────────────────────────────────────────────────
fc_df = None
fc_gdd_total = 0.0
fc_warning: str | None = None

if harv_date >= today:
    with st.spinner("Fetching Open-Meteo forecast..."):
        try:
            raw_fc = fetch_openmeteo(lat, lon)
        except Exception as exc:
            st.error(f"Open-Meteo request failed: {exc}")
            st.stop()

    mask_fc = (raw_fc["date"] >= today) & (raw_fc["date"] <= harv_date)
    fc_df = raw_fc[mask_fc].copy().reset_index(drop=True)
    fc_df["tmax_eff"] = np.minimum(fc_df["tmax"], tmax_cap)
    fc_df["gdd"] = calc_gdd(fc_df["tmin"].values, fc_df["tmax"].values, tbase, tmax_cap)
    fc_gdd_total = float(fc_df["gdd"].sum())

    if fc_df.empty:
        fc_warning = (
            "No forecast days available in the requested window. "
            "Harvest date may be beyond the 16-day forecast range."
        )
    else:
        fc_max_day = fc_df["date"].max()
        if fc_max_day < harv_date:
            fc_warning = (
                f"Forecast only available to {fc_max_day}. "
                f"Harvest date ({harv_date}) is beyond the 16-day forecast window — "
                "GDD for the gap is not included."
            )
else:
    fc_warning = "Harvest date is before today — no forecast data was used."

# ── Combine totals ────────────────────────────────────────────────────────────
days_plant_to_harv = (harv_date - planting_date).days

if preh_date:
    gdd_plant_to_preh = obs_plant_to_preh
    if fc_df is not None and not fc_df.empty and preh_date >= today:
        mask_fc_preh = (fc_df["date"] >= today) & (fc_df["date"] <= preh_date)
        gdd_plant_to_preh += float(fc_df.loc[mask_fc_preh, "gdd"].sum())

    gdd_preh_to_harv = obs_preh_to_lastobs + fc_gdd_total
    gdd_plant_to_harv = gdd_plant_to_preh + gdd_preh_to_harv

    days_plant_to_preh = (preh_date - planting_date).days
    days_preh_to_harv = (harv_date - preh_date).days
else:
    gdd_plant_to_harv = obs_plant_to_harv + fc_gdd_total

# ── Warnings ──────────────────────────────────────────────────────────────────
if planting_date > obs_last_day:
    st.markdown(
        warn_box(
            f"Planting date ({planting_date}) is after the last SILO observed day "
            f"({obs_last_day}). Observed GDD is 0."
        ),
        unsafe_allow_html=True,
    )

if fc_warning:
    st.markdown(warn_box(fc_warning), unsafe_allow_html=True)

# ── Heat stress ───────────────────────────────────────────────────────────────
if heat_stress_on:
    obs_hs = int((wx["maxt"] > heat_stress_temp).sum())
    fc_hs = int((fc_df["tmax"] > heat_stress_temp).sum()) if fc_df is not None and not fc_df.empty else 0
    heat_stress_days = obs_hs + fc_hs
    heat_stress_sub = f"days with Tmax > {heat_stress_temp}°C · {obs_hs} obs + {fc_hs} forecast"

# ── Metrics ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-h">GDD Summary</div>', unsafe_allow_html=True)

if preh_date:
    n_cols = 4 if heat_stress_on else 3
    cols = st.columns(n_cols)
    with cols[0]:
        st.markdown(
            metric_card(
                "GDD — Planting to Pre-harvest",
                f"{gdd_plant_to_preh:.1f}",
                f"°C-days · {days_plant_to_preh} calendar days",
            ),
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            metric_card(
                "GDD — Pre-harvest to Harvest",
                f"{gdd_preh_to_harv:.1f}",
                f"°C-days · {days_preh_to_harv} calendar days",
            ),
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown(
            metric_card(
                "GDD — Planting to Harvest",
                f"{gdd_plant_to_harv:.1f}",
                f"°C-days · {days_plant_to_harv} calendar days",
            ),
            unsafe_allow_html=True,
        )
    if heat_stress_on:
        with cols[3]:
            st.markdown(
                metric_card("Heat Stress Days", str(heat_stress_days), heat_stress_sub),
                unsafe_allow_html=True,
            )
else:
    n_cols = 2 if heat_stress_on else 1
    cols = st.columns(n_cols)
    with cols[0]:
        st.markdown(
            metric_card(
                "GDD — Planting to Harvest",
                f"{gdd_plant_to_harv:.1f}",
                f"°C-days · {days_plant_to_harv} calendar days",
            ),
            unsafe_allow_html=True,
        )
    if heat_stress_on:
        with cols[1]:
            st.markdown(
                metric_card("Heat Stress Days", str(heat_stress_days), heat_stress_sub),
                unsafe_allow_html=True,
            )

# ── Run details ───────────────────────────────────────────────────────────────
with st.expander("Run details"):
    loc_label = loc_name if loc_name != "Custom" else f"Custom ({lat}, {lon})"
    st.markdown(
        f"""
| Parameter | Value |
|---|---|
| Location | {loc_label} |
| Latitude / Longitude | {lat}, {lon} |
| Tbase | {tbase} °C |
| Tmax cap | {tmax_cap} °C |
| SILO observed last day | {obs_last_day} |
| Today (Brisbane) | {today} |
| Planting date | {planting_date} |
| Pre-harvest date | {preh_date if preh_date else "—"} |
| Harvest date | {harv_date} |
"""
    )

# ── Accumulation chart ────────────────────────────────────────────────────────
st.markdown('<div class="section-h">GDD Accumulation Chart</div>', unsafe_allow_html=True)

obs_chart = wx[(wx["date"] >= planting_date) & (wx["date"] <= harv_date)].copy()
obs_chart["cumulative_gdd"] = obs_chart["gdd"].cumsum()

obs_x = [str(d) for d in obs_chart["date"]]
obs_y = obs_chart["cumulative_gdd"].round(1).tolist()

fc_x: list[str] = []
fc_y: list[float] = []
if fc_df is not None and not fc_df.empty:
    obs_end_cum = obs_y[-1] if obs_y else 0.0
    fc_cumsum = (fc_df["gdd"].cumsum() + obs_end_cum).round(1)
    if obs_x:
        fc_x = [obs_x[-1]] + [str(d) for d in fc_df["date"]]
        fc_y = [obs_y[-1]] + fc_cumsum.tolist()
    else:
        fc_x = [str(d) for d in fc_df["date"]]
        fc_y = fc_cumsum.tolist()

fig = go.Figure()

if obs_x:
    fig.add_trace(
        go.Scatter(
            x=obs_x,
            y=obs_y,
            name="Observed (SILO)",
            mode="lines",
            line=dict(color="#2e7d32", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(46,125,50,0.10)",
            hovertemplate="<b>%{x}</b><br>Cumulative GDD: %{y:.1f} °C-days (observed)<extra></extra>",
        )
    )

if fc_x:
    fig.add_trace(
        go.Scatter(
            x=fc_x,
            y=fc_y,
            name="Forecast (Open-Meteo)",
            mode="lines",
            line=dict(color="#1565c0", width=2.5, dash="dash"),
            hovertemplate="<b>%{x}</b><br>Cumulative GDD: %{y:.1f} °C-days (forecast)<extra></extra>",
        )
    )


def vline(
    fig: go.Figure,
    x_date,
    label: str,
    color: str,
    dash: str = "dash",
    label_y: float = 0.95,
    label_xanchor: str = "left",
) -> None:
    """Draw a vertical line + label using add_shape/add_annotation.

    Using add_shape avoids the add_vline internal arithmetic that causes
    date-axis offset errors. ISO date strings are accepted directly by both
    add_shape and add_annotation, so every line lands exactly on its date.
    Labels are placed at alternating heights (paper coords 0–1) so they
    never overlap regardless of how close dates are to each other.
    """
    x_str = str(x_date)
    fig.add_shape(
        type="line",
        x0=x_str, x1=x_str,
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color=color, width=2, dash=dash),
    )
    fig.add_annotation(
        x=x_str,
        xref="x",
        y=label_y,
        yref="paper",
        text=f"<b>{label}</b>",
        showarrow=False,
        xanchor=label_xanchor,
        yanchor="bottom",
        font=dict(size=12, color=color),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor=color,
        borderwidth=1,
        borderpad=4,
    )


# Labels at alternating heights so they never overlap even when dates are close.
# Planted=top-left, Pre-harvest=bottom-right, Today=bottom-left, Harvest=top-right.
vline(fig, planting_date, "Planted",     "#1b5e20", "dot",  label_y=0.95, label_xanchor="left")
if preh_date:
    vline(fig, preh_date, "Pre-harvest", "#6a1b9a", "dash", label_y=0.05, label_xanchor="right")
if today <= harv_date:
    vline(fig, today,     "Today",       "#1565c0", "dash", label_y=0.05, label_xanchor="left")
vline(fig, harv_date,     "Harvest",     "#b71c1c", "dash", label_y=0.95, label_xanchor="right")

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Cumulative GDD (°C-days)",
    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="closest",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(l=0, r=0, t=50, b=20),
    height=440,
)
fig.update_xaxes(
    showgrid=True,
    gridcolor="#f0f0f0",
    range=[str(planting_date), str(harv_date)],
    showspikes=False,
)
fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

# ── Observed table ────────────────────────────────────────────────────────────
st.markdown('<div class="section-h">Observed Data (SILO)</div>', unsafe_allow_html=True)

obs_display = (
    wx[["date", "mint", "maxt", "tmax_eff", "gdd"]]
    .copy()
    .rename(columns={
        "date": "Date",
        "mint": "Min Temp (°C)",
        "maxt": "Max Temp (°C)",
        "tmax_eff": "Tmax Eff (°C)",
        "gdd": "GDD (°C-days)",
    })
)
for col in ["Min Temp (°C)", "Max Temp (°C)", "Tmax Eff (°C)", "GDD (°C-days)"]:
    obs_display[col] = obs_display[col].round(2)
obs_display["Date"] = obs_display["Date"].astype(str)


def style_tmax(df):
    if heat_stress_on:
        return df.style.map(
            lambda v: "background-color: #ffcccc;" if v > heat_stress_temp else "",
            subset=["Max Temp (°C)"],
        )
    return df.style


st.markdown(f"**Last 20 days** of {len(obs_display)} total observed days:")
st.dataframe(style_tmax(obs_display.tail(20)), use_container_width=True, hide_index=True)

with st.expander(f"Show all {len(obs_display)} observed days"):
    st.dataframe(style_tmax(obs_display), use_container_width=True, hide_index=True)

# ── Forecast table ────────────────────────────────────────────────────────────
st.markdown('<div class="section-h">Forecast Data (Open-Meteo)</div>', unsafe_allow_html=True)

if fc_df is None or fc_df.empty:
    st.markdown(
        warn_box("No forecast data available for the selected date range."),
        unsafe_allow_html=True,
    )
else:
    fc_display = (
        fc_df[["date", "tmin", "tmax", "tmax_eff", "gdd"]]
        .copy()
        .rename(columns={
            "date": "Date",
            "tmin": "Min Temp (°C)",
            "tmax": "Max Temp (°C)",
            "tmax_eff": "Tmax Eff (°C)",
            "gdd": "GDD (°C-days)",
        })
    )
    for col in ["Min Temp (°C)", "Max Temp (°C)", "Tmax Eff (°C)", "GDD (°C-days)"]:
        fc_display[col] = fc_display[col].round(2)
    fc_display["Date"] = fc_display["Date"].astype(str)
    st.dataframe(style_tmax(fc_display), use_container_width=True, hide_index=True)

st.markdown(FOOTER_HTML, unsafe_allow_html=True)
