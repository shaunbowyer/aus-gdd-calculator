"""utils.py — Shared utilities for the Agronomy Tools Streamlit app."""

import re
from datetime import date
from io import StringIO

import numpy as np
import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Location presets
# ---------------------------------------------------------------------------
LOCATIONS: dict[str, dict] = {
    "Kalbar":      {"lat": -27.9488, "lon": 152.5790},
    "Warwick":     {"lat": -28.2190, "lon": 152.0340},
    "Tent Hill":   {"lat": -27.5970, "lon": 152.5820},
    "Forest Hill": {"lat": -27.5700, "lon": 152.3600},
    "Bowen":       {"lat": -20.0130, "lon": 148.2470},
}
LOCATION_NAMES = list(LOCATIONS.keys()) + ["Custom"]

# ---------------------------------------------------------------------------
# Shared CSS (injected on every page)
# ---------------------------------------------------------------------------
PAGE_CSS = """
<style>
/* ── Layout ── */
.block-container { padding-top: 1.25rem; }

/* ── Metric cards ── */
.metric-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 1rem 1.25rem 0.9rem;
    border-left: 5px solid #2e7d32;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    height: 100%;
}
.mc-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #777;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.25rem;
}
.mc-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #1b5e20;
    line-height: 1.1;
}
.mc-sub {
    font-size: 0.78rem;
    color: #999;
    margin-top: 0.2rem;
}

/* ── Warning / note boxes ── */
.warn-box {
    background: #fff8e1;
    border-left: 4px solid #f9a825;
    border-radius: 6px;
    padding: 0.65rem 1rem;
    font-size: 0.88rem;
    color: #5d4037;
    margin: 0.5rem 0;
}
.info-box {
    background: #e8f5e9;
    border-left: 4px solid #388e3c;
    border-radius: 6px;
    padding: 0.65rem 1rem;
    font-size: 0.88rem;
    color: #1b5e20;
    margin: 0.5rem 0;
}

/* ── Section headers ── */
.section-h {
    font-size: 1.05rem;
    font-weight: 700;
    color: #2e7d32;
    border-bottom: 2px solid #e8f5e9;
    padding-bottom: 0.35rem;
    margin: 1.4rem 0 0.75rem;
}

/* ── Page footer ── */
.page-footer {
    text-align: center;
    font-size: 0.75rem;
    color: #bbb;
    padding: 1.5rem 0 0.5rem;
    margin-top: 2rem;
    border-top: 1px solid #f0f0f0;
}
</style>
"""

FOOTER_HTML = (
    '<div class="page-footer">'
    "Created by Shaun Bowyer&nbsp;|&nbsp;"
    '<a href="mailto:shaunbowyeragronomy@gmail.com" style="color:#bbb; text-decoration:none;">'
    "shaunbowyeragronomy@gmail.com</a>"
    "</div>"
)


def metric_card(label: str, value: str, sub: str = "") -> str:
    """Return an HTML metric card string for use with st.markdown(unsafe_allow_html=True)."""
    sub_html = f'<div class="mc-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="metric-card">'
        f'<div class="mc-label">{label}</div>'
        f'<div class="mc-value">{value}</div>'
        f"{sub_html}"
        f"</div>"
    )


def warn_box(msg: str) -> str:
    return f'<div class="warn-box">{msg}</div>'


def info_box(msg: str) -> str:
    return f'<div class="info-box">{msg}</div>'


# ---------------------------------------------------------------------------
# Date / coordinate helpers
# ---------------------------------------------------------------------------
def today_brisbane() -> date:
    """Return today's date in Brisbane time (AEST, UTC+10, no DST)."""
    import datetime
    import pytz

    tz = pytz.timezone("Australia/Brisbane")
    return datetime.datetime.now(tz).date()


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email.strip()))


# ---------------------------------------------------------------------------
# GDD calculation
# ---------------------------------------------------------------------------
def calc_gdd(
    tmin: "np.ArrayLike",
    tmax: "np.ArrayLike",
    tbase: float,
    tmax_cap: float,
) -> np.ndarray:
    """GDD = max(0, (min(tmax, tmax_cap) + tmin) / 2 − tbase)."""
    tmax_eff = np.minimum(np.asarray(tmax, dtype=float), tmax_cap)
    return np.maximum(0.0, (tmax_eff + np.asarray(tmin, dtype=float)) / 2.0 - tbase)


# ---------------------------------------------------------------------------
# SILO DataDrill — APSIM format
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_silo(
    lat: float,
    lon: float,
    email: str,
    start_str: str,   # "YYYYMMDD"
    end_str: str,     # "YYYYMMDD"
) -> pd.DataFrame:
    """
    Fetch SILO DataDrill data in APSIM format and return a tidy DataFrame.

    Returned columns include at minimum:
        date (datetime.date), mint (°C), maxt (°C)
    plus all other APSIM columns (radn, rain, evap, vp, code …).
    """
    url = "https://www.longpaddock.qld.gov.au/cgi-bin/silo/DataDrillDataset.php"
    params = {
        "start": start_str,
        "finish": end_str,
        "lat": lat,
        "lon": lon,
        "format": "apsim",
        "username": email,
        "password": "apitest",
    }

    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()

    lines = r.text.splitlines()

    # Find the column header row (starts with "year")
    header_idx = next(
        (i for i, ln in enumerate(lines) if ln.strip().lower().startswith("year")),
        None,
    )
    if header_idx is None:
        raise ValueError(
            "Could not find the data header in the SILO response. "
            "Check your email address and that the date range is valid."
        )

    df = pd.read_csv(StringIO("\n".join(lines[header_idx:])), sep=r"\s+")
    df.columns = [c.lower() for c in df.columns]

    for col in ("year", "day", "maxt", "mint"):
        if col not in df.columns:
            raise ValueError(f"SILO response is missing expected column '{col}'.")

    # The APSIM format includes a units row immediately after the header
    # (e.g. "()", "(MJ/m^2)", "(oC)") — drop any rows where 'year' is not numeric.
    df = df[pd.to_numeric(df["year"], errors="coerce").notna()].copy()
    df["year"] = df["year"].astype(int)
    df["day"] = df["day"].astype(int)
    df["maxt"] = pd.to_numeric(df["maxt"], errors="coerce")
    df["mint"] = pd.to_numeric(df["mint"], errors="coerce")

    # Convert year + day-of-year → datetime.date
    df["date"] = pd.to_datetime(
        df["year"].astype(str) + df["day"].astype(str).str.zfill(3),
        format="%Y%j",
    ).dt.date

    return df


# ---------------------------------------------------------------------------
# Open-Meteo 16-day forecast
# ---------------------------------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_openmeteo(lat: float, lon: float) -> pd.DataFrame:
    """
    Fetch 16-day daily temperature forecast from Open-Meteo (Brisbane timezone).

    Returns DataFrame with columns: date (datetime.date), tmax (°C), tmin (°C).
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&temperature_unit=celsius"
        f"&timezone=Australia%2FBrisbane"
        f"&forecast_days=16"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    data = r.json()
    daily = data.get("daily") or {}
    if "time" not in daily:
        raise ValueError("Open-Meteo returned no daily forecast data.")

    return pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]).date,
            "tmax": np.array(daily["temperature_2m_max"], dtype=float),
            "tmin": np.array(daily["temperature_2m_min"], dtype=float),
        }
    )
