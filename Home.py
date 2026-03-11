"""app.py — Agronomy Tools home page."""

import streamlit as st

st.set_page_config(
    page_title="Agronomy Tools",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
.block-container { padding-top: 1.25rem; }

.hero {
    background: linear-gradient(135deg, #1b5e20 0%, #388e3c 60%, #43a047 100%);
    border-radius: 14px;
    padding: 2.2rem 2.5rem;
    color: white;
    margin-bottom: 2rem;
}
.hero h1 { margin: 0; font-size: 2.4rem; font-weight: 800; }
.hero p  { margin: 0.5rem 0 0; font-size: 1.05rem; opacity: 0.88; }

/* Equal-height columns — cascade through every Streamlit wrapper div */
div[data-testid="stHorizontalBlock"] {
    display: flex;
    align-items: stretch;
    margin-bottom: 2rem;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    display: flex;
    flex-direction: column;
    flex: 1;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
    display: flex;
    flex-direction: column;
    flex: 1;
    position: relative; /* anchor for the button overlay */
}
div[data-testid="stHorizontalBlock"] .stMarkdown {
    flex: 1;
    display: flex;
    flex-direction: column;
}

/* Transparent full-area button overlay for card click */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] {
    position: absolute;
    inset: 0;
    z-index: 10;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    width: 100%;
    height: 100%;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    cursor: pointer;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover,
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:focus {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

.tool-card {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    box-shadow: 0 3px 12px rgba(0,0,0,0.07);
    flex: 1;
    transition: box-shadow 0.2s, border-color 0.2s, transform 0.15s;
}
/* Hover triggered on the column block (button intercepts the mouse) */
div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"]:hover .tool-card {
    box-shadow: 0 8px 28px rgba(0,0,0,0.15);
    border-color: #2e7d32;
    transform: translateY(-2px);
}
.tool-card h3 { color: #2e7d32; margin-top: 0; font-size: 1.2rem; }
.tool-card p  { color: #555; font-size: 0.93rem; line-height: 1.55; }
.tool-card ul { color: #555; font-size: 0.9rem; padding-left: 1.2rem; }
.tool-card ul li { margin-bottom: 0.3rem; }

.badge {
    display: inline-block;
    background: #e8f5e9;
    color: #2e7d32;
    border-radius: 20px;
    padding: 0.15rem 0.7rem;
    font-size: 0.75rem;
    font-weight: 700;
    margin-right: 0.4rem;
    margin-bottom: 0.6rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
    <h1>Australian Observed and Forecasted GDD Calculator</h1>
    <p>Completely free &nbsp;·&nbsp; SILO observed data &nbsp;·&nbsp; Open-Meteo 16-day forecast</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Tool cards ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        """
<div class="tool-card">
    <h3>Observed GDD</h3>
    <p>Calculate Growing Degree Days accumulated from your planting date using
    historical SILO weather observations.</p>
    <span class="badge">SILO DataDrill</span>
    <span class="badge">Historical</span>
    <ul>
        <li>Observed daily min &amp; max temperatures</li>
        <li>Customisable T<sub>base</sub> and T<sub>max</sub> cap</li>
        <li>Preset Queensland locations + custom coordinates</li>
        <li>Cumulative GDD chart &amp; daily data table</li>
    </ul>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("", key="btn_observed", use_container_width=True):
        st.switch_page("pages/1_Observed_GDD.py")

with col2:
    st.markdown(
        """
<div class="tool-card">
    <h3>Observed + Forecasted GDD</h3>
    <p>Project GDD through to harvest by combining SILO historical observations
    with the Open-Meteo 16-day temperature forecast.</p>
    <span class="badge">SILO DataDrill</span>
    <span class="badge">Open-Meteo Forecast</span>
    <ul>
        <li>SILO observed up to yesterday (Brisbane time)</li>
        <li>Open-Meteo 16-day daily forecast from today</li>
        <li>GDD segments: Planting → Pre-harvest → Harvest</li>
        <li>Forecast cutoff warning if harvest is beyond 16 days</li>
    </ul>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("", key="btn_forecasted", use_container_width=True):
        st.switch_page("pages/2_Observed_Forecasted_GDD.py")

# ── Footer ────────────────────────────────────────────────────────────────────
st.info("Select a tool from the sidebar to get started.")
st.markdown("---")
st.markdown(
    """
<div style="color:#aaa; font-size:0.82rem; text-align:center; padding-bottom:1rem;">
    Data sources: <a href="https://www.longpaddock.qld.gov.au/silo/" style="color:#888;">SILO (Queensland Government)</a>
    &nbsp;·&nbsp;
    <a href="https://open-meteo.com/" style="color:#888;">Open-Meteo</a>
    &nbsp;·&nbsp; Requires a valid email address for SILO requests.
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div style="text-align:center; font-size:0.75rem; color:#bbb; padding:1.5rem 0 0.5rem;
            margin-top:2rem; border-top:1px solid #f0f0f0;">
    Created by Shaun Bowyer&nbsp;|&nbsp;
    <a href="mailto:shaunbowyeragronomy@gmail.com" style="color:#bbb; text-decoration:none;">
    shaunbowyeragronomy@gmail.com</a>
</div>
""",
    unsafe_allow_html=True,
)
