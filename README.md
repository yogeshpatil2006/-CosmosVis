# 🛰️ CosmosVis — Global Space Missions & Satellite Tracker

> **M.Sc. Computer Science Interactive Visual Analytics Mini-Project.**  
> Transforming Authentic Historical Orbital Data (1957–2020) into Interactive Visual Intelligence.

CosmosVis is an academic-grade aerospace visual analytics dashboard built strictly using the **six approved technologies**:
1. **Python** (Core runtime & data structures)
2. **Streamlit** (Native reactive web application framework)
3. **Pandas** (High-performance dataset cleaning, grouping & filtering)
4. **NumPy** (Numerical vectorization & regression calculations)
5. **Plotly** (Interactive WebGL/SVG visualization engine)
6. **Geopy** (WGS-84 ellipsoidal geodesics & great-circle navigation)

**100% Authentic Data — Zero Synthetic or Fabricated Records.**

---

## 🌟 Key Objectives & Core Analytical Features

1. **📈 Objective 1: Historical Timeline & Eras**
   - **Chronological Mapping:** Traces orbital launches from the dawn of the Space Age (Sputnik 1 in 1957) through Apollo, the Space Shuttle and Mir eras, up to modern commercial megaconstellations.
   - **Missions by Decade:** Interactive decadal volume trajectory (`1950s` to `2020s`).
   - **Era Distribution:** Vertical bar chart detailing flight volume across major space exploration eras with success rate telemetry and plain-text angled labels.
   - **Annual Launch Trajectory:** Area chart showing annual launch frequency decomposed by Country or Aerospace Company.

2. **🎯 Objective 2: Success Rate & Flight Reliability**
   - **Hierarchical Outcome Drilldowns:** Multi-level **Sunburst** and **Treemap** visualizations decomposing missions by `Country → Outcome (Success, Failure, Partial Failure, Prelaunch Failure)`.
   - **National Reliability Benchmarks:** Benchmarks flight success rates across sovereign space programs (USA, Russia, China, France/ESA, India, Japan, etc.) with launch count annotations.
   - **Decadal Reliability Curve:** Visualizes historical flight reliability improvements from ~75% in the late 1950s to >95% in modern spaceflight.

3. **💰 Objective 3: Launch Cost & Financial Telemetry**
   - **Transparent Historical Accounting:** Analyzes the 964 missions with reported budget figures without imputing artificial numbers.
   - **Cost vs. Time Scatter Plot:** Plots reported launch costs ($M USD) against launch year with pure NumPy OLS linear regression line.
   - **Top 10 Most Expensive Rocket Systems:** Ranks the most capital-intensive launch systems in space history (e.g., Saturn V, Space Shuttle, Titan IV, Energia).
   - **Operator Cost Distributions:** Boxplot comparisons across major launch providers (NASA, Arianespace, ULA, SpaceX, Roscosmos, CASC).

4. **🗺️ Objective 4: Global Spaceports & Geopy Navigation**
   - **Interactive World Map:** High-visibility map tiles (`carto-darkmatter` in Dark mode and `carto-positron` in Light mode) mapping 38 authentic orbital spaceports.
   - **Geopy Geodesic Distance Calculator:** Calculates precise great-circle distances between any two global spaceports in kilometers, statute miles, and nautical miles using WGS-84 ellipsoidal geometry.
   - **Earth Rotation Velocity Assist:** Calculates tangential surface velocity bonus ($v_{rot} = 465.1 \times \cos(\text{latitude})\text{ m/s}$) to explain equatorial launch physics advantages.

5. **🔍 Objective 5: Country Comparison & Mission Search**
   - **Head-to-Head Comparison:** Side-by-side comparative analytics of any two sovereign nations across total launches, success rates, active contractors, and decadal distributions.
   - **Real-Time Mission Search:** Search across rocket names, mission payloads, aerospace companies, and launch sites.

---

## 🎨 Native Light & Dark Theme Support

CosmosVis uses Streamlit's **native Light and Dark theme engine** configured via `.streamlit/config.toml`:
- **Dark Theme:** Deep navy/slate palette (`#0b1120`, `#131d31`) with cyan/teal primary highlights (`#0284c7`).
- **Light Theme:** Clean white and light grey palette with high contrast and readable text.
- **Switching:** Switch seamlessly between themes via Streamlit's native app menu (**Settings → Theme**).
- **Zero HTML/CSS:** Completely free of custom CSS, HTML injection, or `unsafe_allow_html=True`.

---

## 📂 Project Structure

```
cosmosvis/
├── app.py                 # Main Streamlit dashboard (built with native Streamlit components)
├── data_loader.py         # Real dataset ingestion, schema validation, Geopy physics enrichment
├── charts.py              # Plotly visualization engine (pure Python API, plain-text tooltips)
├── utils.py               # Geopy geodesic ellipsoidal calculations & orbital physics helpers
├── requirements.txt       # Exactly the 5 approved packages (streamlit, pandas, numpy, plotly, geopy)
├── run_all_tests.py       # Automated verification test suite (18 test scenarios)
├── .streamlit/
│   └── config.toml        # Native Streamlit dark/light theme configuration
└── README.md              # Academic documentation & setup instructions
```

---

## 🛠️ Quickstart Installation & Execution

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.10, 3.11, 3.12, 3.13)
- pip

### 2. Navigate to Directory
```bash
cd "C:\Users\Yogesh Patil\.gemini\antigravity\scratch\cosmosvis"
```

### 3. Install Approved Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Automated Tests
```bash
python run_all_tests.py
```

### 5. Launch the Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Dataset Schema (`Space_Corrected.csv`)

| Column | Description |
| :--- | :--- |
| `Company Name` | Launch agency or contractor (e.g., *NASA, Roscosmos, SpaceX, ISRO, CASC, ULA*) |
| `Location` | Launch pad facility, territory, and country (mapped to 38 real spaceports) |
| `Datum` | UTC launch date and timestamp (1957–2020) |
| `Detail` | Rocket vehicle model and payload mission name (e.g., *Falcon 9 Block 5 \| Starlink*) |
| `Status Rocket` | Operational status of the vehicle (*StatusActive*, *StatusRetired*) |
| `Rocket` | Disclosed launch cost in Millions USD ($M) (reported for 964 flights) |
| `Status Mission` | Flight outcome (*Success*, *Failure*, *Partial Failure*, *Prelaunch Failure*) |

Dataset Source: [Kaggle: All Space Missions from 1957](https://www.kaggle.com/datasets/agirlcoding/all-space-missions-from-1957)
