"""app.py — Agronomy Tools home page."""

import streamlit as st

st.set_page_config(
    page_title="Agronomy Tools",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo:wght@400;600;700;800&family=Roboto+Mono:wght@400;500;700&display=swap');

.block-container { padding-top: 1.25rem; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #052e16 0%, #14532d 40%, #166534 75%, #15803d 100%);
    border-radius: 20px;
    padding: 2.6rem 3rem;
    color: white;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 240px; height: 240px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -70px; left: 35%;
    width: 320px; height: 320px;
    background: rgba(255,255,255,0.03);
    border-radius: 50%;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.22);
    color: rgba(255,255,255,0.92);
    border-radius: 20px;
    padding: 0.22rem 0.9rem;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    font-family: 'Exo', system-ui, sans-serif;
    position: relative; z-index: 1;
}
.hero h1 {
    font-family: 'Exo', system-ui, sans-serif;
    margin: 0;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    position: relative; z-index: 1;
}
.hero p {
    margin: 0.65rem 0 0;
    font-size: 1rem;
    opacity: 0.82;
    max-width: 560px;
    line-height: 1.6;
    position: relative; z-index: 1;
}
.hero-pills {
    margin-top: 1.2rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    position: relative; z-index: 1;
}
.hero-pill {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.18);
    color: rgba(255,255,255,0.85);
    border-radius: 14px;
    padding: 0.2rem 0.7rem;
    font-size: 0.72rem;
    font-family: 'Roboto Mono', monospace;
}

/* ── Tool cards ── */
.cards-row {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
}
.tool-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 1.8rem 2rem 2rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    flex: 1;
    transition: box-shadow 0.22s, border-color 0.22s, transform 0.15s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.tool-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #166534, #4ade80);
    border-radius: 18px 18px 0 0;
}
.tool-card:hover {
    box-shadow: 0 10px 36px rgba(0,0,0,0.12);
    border-color: #86efac;
    transform: translateY(-3px);
}
.card-icon {
    width: 44px; height: 44px;
    background: #f0fdf4;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 1rem;
}
.tool-card h3 {
    font-family: 'Exo', system-ui, sans-serif;
    color: #166534;
    margin: 0 0 0.5rem 0;
    font-size: 1.2rem;
    font-weight: 700;
}
.tool-card p  { color: #475569; font-size: 0.92rem; line-height: 1.6; margin: 0 0 0.9rem; }
.tool-card ul { color: #475569; font-size: 0.875rem; padding-left: 1.15rem; margin: 0; }
.tool-card ul li { margin-bottom: 0.35rem; }

/* ── Badges ── */
.badges { margin-bottom: 0.9rem; }
.badge {
    display: inline-block;
    background: #f0fdf4;
    color: #166534;
    border: 1px solid #86efac;
    border-radius: 20px;
    padding: 0.18rem 0.75rem;
    font-size: 0.7rem;
    font-weight: 700;
    font-family: 'Exo', system-ui, sans-serif;
    letter-spacing: 0.04em;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

/* ── Info tip ── */
.start-tip {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-left: 4px solid #16a34a;
    border-radius: 10px;
    padding: 0.75rem 1.1rem;
    font-size: 0.875rem;
    color: #14532d;
    margin-bottom: 1.5rem;
    font-family: 'Exo', system-ui, sans-serif;
}

/* ── Footer ── */
.home-footer {
    text-align: center;
    font-size: 0.75rem;
    color: #94a3b8;
    padding: 1.5rem 0 0.5rem;
    margin-top: 1rem;
    border-top: 1px solid #e2e8f0;
    font-family: 'Exo', system-ui, sans-serif;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
    <div class="hero-badge">Australia &nbsp;·&nbsp; Free &nbsp;·&nbsp; Open Data</div>
    <h1>Australian GDD Calculator</h1>
    <p>Growing Degree Day tools for Australian growers — powered by real observed data
    and 16-day weather forecasts.</p>
    <div class="hero-pills">
        <span class="hero-pill">SILO DataDrill</span>
        <span class="hero-pill">Open-Meteo 16-day</span>
        <span class="hero-pill">Custom T&#x2090;ase &amp; T&#x2098;&#x2090;&#x2093; cap</span>
        <span class="hero-pill">Heat stress tracking</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Tip ───────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="start-tip">Select a tool from the sidebar to get started.</div>',
    unsafe_allow_html=True,
)

# ── Tool cards ────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="cards-row">

  <div class="tool-card" onclick="window.top.location.href='/Observed_GDD'">
    <div class="card-icon">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#166534" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>
      </svg>
    </div>
    <h3>Observed GDD</h3>
    <div class="badges">
      <span class="badge">SILO DataDrill</span>
      <span class="badge">Historical</span>
    </div>
    <p>Calculate Growing Degree Days accumulated from your planting date using
    historical SILO weather observations.</p>
    <ul>
      <li>Observed daily min &amp; max temperatures</li>
      <li>Customisable T<sub>base</sub> and T<sub>max</sub> cap</li>
      <li>Preset Queensland locations + custom coordinates</li>
      <li>Cumulative GDD chart &amp; daily data table</li>
      <li>Optional heat stress day counter</li>
    </ul>
  </div>

  <div class="tool-card" onclick="window.top.location.href='/Observed_+_Forecasted_GDD'">
    <div class="card-icon">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#166534" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>
        <path d="m16 14 3-3" stroke-dasharray="3 2"/>
      </svg>
    </div>
    <h3>Observed + Forecasted GDD</h3>
    <div class="badges">
      <span class="badge">SILO DataDrill</span>
      <span class="badge">Open-Meteo Forecast</span>
    </div>
    <p>Project GDD through to harvest by combining SILO historical observations
    with the Open-Meteo 16-day temperature forecast.</p>
    <ul>
      <li>SILO observed up to yesterday (Brisbane time)</li>
      <li>Open-Meteo 16-day daily forecast from today</li>
      <li>GDD segments: Planting &rarr; Pre-harvest &rarr; Harvest</li>
      <li>Forecast cutoff warning if harvest is beyond 16 days</li>
      <li>Optional heat stress day counter</li>
    </ul>
  </div>

</div>
""",
    unsafe_allow_html=True,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="home-footer">
    Created by Shaun Bowyer&nbsp;·&nbsp;
    <a href="mailto:shaunbowyeragronomy@gmail.com" style="color:#94a3b8; text-decoration:none;">
    shaunbowyeragronomy@gmail.com</a>
    &nbsp;·&nbsp;
    Data: <a href="https://www.longpaddock.qld.gov.au/silo/" style="color:#94a3b8; text-decoration:none;">SILO (Queensland Government)</a>
    &nbsp;&amp;&nbsp;
    <a href="https://open-meteo.com/" style="color:#94a3b8; text-decoration:none;">Open-Meteo</a>
    &nbsp;·&nbsp; Requires a valid email address for SILO requests.
</div>
""",
    unsafe_allow_html=True,
)
