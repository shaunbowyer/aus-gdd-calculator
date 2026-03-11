# 🌱 Australian GDD Calculator

**A free, web-based Growing Degree Days (GDD) calculator for Australian agronomists and crop consultants.**

Built with real observed weather data from SILO and 16-day forecasts from Open-Meteo, this tool helps you track and project heat accumulation from planting through to harvest — for any crop with known GDD requirements.

🔗 **Live app: [aus-gdd-calculator.streamlit.app](https://shaunbowyer-aus-gdd-calculator.streamlit.app)**

---

## What is GDD?

Growing Degree Days (GDD) is a measure of heat accumulation used to predict crop development stages. By tracking the difference between daily temperatures and a base temperature (Tbase), agronomists can estimate when a crop will reach key milestones such as flowering, maturity, or harvest readiness.

---

## Features

- 📡 **SILO observed data** — pulls real historical daily min/max temperatures from the Queensland Government's SILO DataDrill API
- 🔮 **Open-Meteo 16-day forecast** — extends GDD projections beyond today using a free, high-accuracy weather forecast
- 🗺️ **Interactive satellite map** — visualise your selected location using Esri World Imagery
- 📍 **Preset Queensland locations** — Kalbar, Warwick, Tent Hill, Forest Hill, Bowen
- 📌 **Custom coordinates** — enter any Australian lat/lon for site-specific analysis
- 📊 **GDD Accumulation Chart** — visualise observed vs forecasted GDD over the full season
- 🌡️ **Customisable Tbase and Tmax cap** — works for any crop with GDD requirements
- 📅 **Three-phase breakdown** — Planting → Pre-harvest → Harvest GDD segments

---

## How to Use

1. Select a location or enter custom coordinates
2. Enter your planting date, pre-harvest date, and harvest date
3. Enter your email address (required for SILO API access)
4. Set your Tbase (°C) and Tmax cap (°C) for your crop
5. Click **Calculate GDD**

No account or subscription required — completely free.

---

## GDD Formula

```
Daily GDD = max(0, ((min(Tmax, Tmax_cap) + Tmin) / 2) - Tbase)
```

Cumulative GDD is summed from planting date through to the selected end date.

---

## Data Sources

- **SILO DataDrill** — [Queensland Government](https://www.longpaddock.qld.gov.au/silo/) — observed daily weather data across Australia
- **Open-Meteo** — [open-meteo.com](https://open-meteo.com) — free 16-day weather forecast API

---

## Tech Stack

- [Streamlit](https://streamlit.io) — web app framework
- [Pandas](https://pandas.pydata.org) — data processing
- [Plotly](https://plotly.com) — interactive charts
- [Folium](https://python-visualization.github.io/folium/) + [streamlit-folium](https://github.com/randyzwitch/streamlit-folium) — interactive maps
- [Requests](https://requests.readthedocs.io) — API calls

---

## Local Development

```bash
git clone https://github.com/shaunbowyer/aus-gdd-calculator.git
cd aus-gdd-calculator
pip install -r requirements.txt
streamlit run Home.py
```

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

---

## Contact

Created by **Shaun Bowyer**
📧 shaunbowyeragronomy@gmail.com
