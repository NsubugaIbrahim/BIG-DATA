import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Patent Analytics Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# FRIENDLY MODERN CSS
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root{
    --bg:#07111f;
    --card:#0d1b2a;
    --card2:#12243a;
    --cyan:#00F5FF;
    --cyan-soft:#7eeeff;
    --pink:#ff4fd8;
    --green:#00ff9d;
    --text:#f3f7ff;
    --muted:#9db7d3;
}

/* =====================================================
GLOBAL
===================================================== */

html, body, [class*="css"]{
    font-family:'Inter', sans-serif;
}

.stApp{
    background:
        radial-gradient(circle at top left,
        rgba(0,245,255,0.08), transparent 30%),

        radial-gradient(circle at bottom right,
        rgba(255,79,216,0.06), transparent 25%),

        linear-gradient(180deg,#050b16 0%, #07111f 100%);

    color:white;
}

/* subtle grid */

.stApp::before{
    content:"";
    position:fixed;
    inset:0;

    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);

    background-size:40px 40px;

    pointer-events:none;
    z-index:0;
}

/* =====================================================
HEADINGS
===================================================== */

h1{
    color:var(--cyan) !important;
    font-size:3rem !important;
    font-weight:700 !important;

    text-shadow:
        0 0 10px rgba(0,245,255,0.4),
        0 0 25px rgba(0,245,255,0.15);
}

h2{
    color:var(--cyan-soft) !important;
    font-weight:600 !important;
}

h3{
    color:white !important;
    font-weight:600 !important;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"]{
    background:
        linear-gradient(
            180deg,
            #0a1422 0%,
            #0d1b2a 100%
        );

    border-right:
        1px solid rgba(0,245,255,0.12);
}

/* =====================================================
METRIC CARDS
===================================================== */

[data-testid="stMetric"]{
    background:rgba(13,27,42,0.75);

    border:
        1px solid rgba(0,245,255,0.14);

    border-radius:18px;

    padding:18px;

    backdrop-filter:blur(12px);

    box-shadow:
        0 0 20px rgba(0,245,255,0.04);
}

[data-testid="stMetricValue"]{
    color:var(--cyan);
    font-weight:700;
}

/* =====================================================
CUSTOM SLIDER
===================================================== */

.stSlider{
    background:
        rgba(0,245,255,0.03);

    padding:15px;

    border-radius:16px;

    border:
        1px solid rgba(0,245,255,0.1);
}

/* track */

.stSlider > div > div > div > div{
    background:
        rgba(255,255,255,0.08) !important;

    height:10px !important;

    border-radius:999px !important;
}

/* active range */

.stSlider > div > div > div > div > div{
    background:
        linear-gradient(
            90deg,
            #00F5FF,
            #00D9FF,
            #62f7ff
        ) !important;

    box-shadow:
        0 0 12px rgba(0,245,255,0.5);
}

/* slider thumb */

.stSlider [role="slider"]{
    background:white !important;

    border:
        3px solid #00F5FF !important;

    width:22px !important;
    height:22px !important;

    box-shadow:
        0 0 14px rgba(0,245,255,0.7);
}

/* =====================================================
NAV BUTTONS
===================================================== */

.nav-btn{
    display:block;

    width:100%;

    padding:12px 14px;

    margin-bottom:10px;

    border-radius:14px;

    border:
        1px solid rgba(0,245,255,0.12);

    background:
        rgba(255,255,255,0.02);

    color:white !important;

    text-decoration:none !important;

    transition:0.25s ease;

    font-weight:500;
}

.nav-btn:hover{
    background:
        rgba(0,245,255,0.08);

    border-color:
        rgba(0,245,255,0.4);

    transform:
        translateY(-2px);

    box-shadow:
        0 0 16px rgba(0,245,255,0.12);
}

/* =====================================================
PLOTLY CONTAINERS
===================================================== */

.js-plotly-plot{
    border:
        1px solid rgba(0,245,255,0.08);

    border-radius:20px;

    overflow:hidden;

    background:
        rgba(13,27,42,0.55);

    backdrop-filter:blur(8px);
}

/* =====================================================
DATAFRAMES
===================================================== */

[data-testid="stDataFrame"]{
    border-radius:18px;
    overflow:hidden;

    border:
        1px solid rgba(0,245,255,0.08);
}

/* =====================================================
TABS
===================================================== */

.stTabs [data-baseweb="tab"]{
    font-size:16px;
    font-weight:600;
}

/* =====================================================
FOOTER
===================================================== */

footer{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================

st.title("🌍 Global Patent Analytics Platform")

st.markdown("""
<div style="
font-size:1.05rem;
color:#9db7d3;
margin-bottom:25px;
">
Descriptive • Diagnostic • Predictive • Prescriptive Analytics
</div>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    top_inventors = pd.read_csv("top_inventors.csv")
    top_companies = pd.read_csv("top_companies.csv")
    year_trends = pd.read_csv("year_trends.csv")

    try:
        top_countries = pd.read_csv("top_countries.csv")
    except:
        top_countries = pd.DataFrame()

    return (
        top_inventors,
        top_companies,
        year_trends,
        top_countries
    )

top_inventors, top_companies, trends, top_countries = load_data()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("⚡ Dashboard Controls")

min_year = int(trends['year'].min())
max_year = int(trends['year'].max())

st.sidebar.markdown("""
<div style="
font-size:0.95rem;
color:#9db7d3;
margin-bottom:8px;
">
Select timeline range
</div>
""", unsafe_allow_html=True)

year_range = st.sidebar.slider(
    "",
    min_year,
    max_year,
    (min_year, max_year)
)

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.markdown("---")
st.sidebar.subheader("🧭 Navigation")

sections = [
    ("📊 KPI Overview", "#kpi"),
    ("📈 Growth Trends", "#growth"),
    ("🏆 Inventors & Companies", "#inventors"),
    ("🌎 Country Analytics", "#countries"),
    ("🔍 Diagnostics", "#diagnostics"),
    ("🔥 Heatmap", "#heatmap"),
    ("🔮 Forecasting", "#forecast"),
    ("🧠 Recommendations", "#recommend"),
    ("📁 Raw Data", "#rawdata")
]

for label, link in sections:
    st.sidebar.markdown(
        f'<a class="nav-btn" href="{link}">{label}</a>',
        unsafe_allow_html=True
    )

# =====================================================
# FILTER DATA
# =====================================================

filtered_trends = trends[
    (trends['year'] >= year_range[0]) &
    (trends['year'] <= year_range[1])
].copy()

# =====================================================
# KPI SECTION
# =====================================================

st.markdown('<div id="kpi"></div>', unsafe_allow_html=True)

total_patents = int(filtered_trends['total_patents'].sum())

avg_patents = int(
    filtered_trends['total_patents'].mean()
)

peak_year = int(
    filtered_trends.loc[
        filtered_trends['total_patents'].idxmax()
    ]['year']
)

growth_rate = round(
    (
        filtered_trends['total_patents'].iloc[-1]
        -
        filtered_trends['total_patents'].iloc[0]
    )
    /
    filtered_trends['total_patents'].iloc[0]
    * 100,
    2
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("📄 Total Patents", f"{total_patents:,}")
k2.metric("📈 Avg / Year", f"{avg_patents:,}")
k3.metric("🚀 Growth Rate", f"{growth_rate}%")
k4.metric("🏆 Peak Year", peak_year)

# =====================================================
# COMMON PLOT THEME
# =====================================================

PLOT_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)

BAR_COLOR = "#00D9FF"

# =====================================================
# PATENT GROWTH
# =====================================================

st.markdown("---")
st.markdown('<div id="growth"></div>', unsafe_allow_html=True)

st.header("📈 Patent Growth Trends")

fig_line = px.line(
    filtered_trends,
    x="year",
    y="total_patents",
    markers=True,
    title="Global Patent Growth Over Time"
)

fig_line.update_traces(
    line=dict(width=4, color="#00F5FF"),
    marker=dict(size=8, color="#00F5FF")
)

fig_line.update_layout(**PLOT_LAYOUT)

st.plotly_chart(fig_line, use_container_width=True)

# =====================================================
# INVENTORS + COMPANIES
# =====================================================

st.markdown("---")
st.markdown('<div id="inventors"></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:

    st.subheader("🏆 Top Inventors")

    fig_inv = px.bar(
        top_inventors.head(15),
        x="patent_count",
        y="name",
        orientation="h"
    )

    fig_inv.update_traces(
        marker_color=BAR_COLOR
    )

    fig_inv.update_layout(**PLOT_LAYOUT)

    st.plotly_chart(fig_inv, use_container_width=True)

with col2:

    st.subheader("🏢 Top Companies")

    fig_comp = px.bar(
        top_companies.head(15),
        x="patent_count",
        y="name",
        orientation="h"
    )

    fig_comp.update_traces(
        marker_color=BAR_COLOR
    )

    fig_comp.update_layout(**PLOT_LAYOUT)

    st.plotly_chart(fig_comp, use_container_width=True)

# =====================================================
# COUNTRY ANALYTICS
# =====================================================

if not top_countries.empty:

    st.markdown("---")
    st.markdown('<div id="countries"></div>', unsafe_allow_html=True)

    st.header("🌎 Global Country Analytics")

    c1, c2 = st.columns(2)

    with c1:

        fig_country = px.bar(
            top_countries.head(15),
            x="country",
            y="patent_count",
            title="Top Patent Countries"
        )

        fig_country.update_traces(
            marker_color=BAR_COLOR
        )

        fig_country.update_layout(**PLOT_LAYOUT)

        st.plotly_chart(fig_country, use_container_width=True)

    with c2:

        fig_pie = px.pie(
            top_countries.head(10),
            names="country",
            values="patent_count",
            hole=0.45
        )

        fig_pie.update_layout(**PLOT_LAYOUT)

        st.plotly_chart(fig_pie, use_container_width=True)

# =====================================================
# DIAGNOSTIC ANALYTICS
# =====================================================

st.markdown("---")
st.markdown('<div id="diagnostics"></div>', unsafe_allow_html=True)

st.header("🔍 Diagnostic Analytics")

filtered_trends['rolling_avg'] = (
    filtered_trends['total_patents']
    .rolling(5)
    .mean()
)

fig_diag = go.Figure()

fig_diag.add_trace(go.Scatter(
    x=filtered_trends['year'],
    y=filtered_trends['total_patents'],
    mode='lines+markers',
    name='Actual',
    line=dict(color="#00F5FF", width=4)
))

fig_diag.add_trace(go.Scatter(
    x=filtered_trends['year'],
    y=filtered_trends['rolling_avg'],
    mode='lines',
    name='5-Year Moving Average',
    line=dict(color="#ff4fd8", width=3, dash='dash')
))

fig_diag.update_layout(
    title="Patent Growth Stability",
    **PLOT_LAYOUT
)

st.plotly_chart(fig_diag, use_container_width=True)

# =====================================================
# RESTORED HEATMAP
# =====================================================

st.markdown("---")
st.markdown('<div id="heatmap"></div>', unsafe_allow_html=True)

st.header("🔥 Patent Intensity Heatmap")

heatmap_df = filtered_trends.copy()

heatmap_df['decade'] = (
    heatmap_df['year'] // 10
) * 10

heatmap_summary = heatmap_df.groupby(
    ['decade']
)['total_patents'].sum().reset_index()

fig_heat = px.density_heatmap(
    heatmap_summary,
    x='decade',
    y='total_patents',
    title='Patent Intensity by Decade'
)

fig_heat.update_layout(**PLOT_LAYOUT)

st.plotly_chart(fig_heat, use_container_width=True)

# =====================================================
# AREA CHART
# =====================================================

st.markdown("---")

st.header("🌊 Patent Volume Area Chart")

fig_area = px.area(
    filtered_trends,
    x="year",
    y="total_patents"
)

fig_area.update_traces(
    line=dict(color="#00ff9d", width=3)
)

fig_area.update_layout(**PLOT_LAYOUT)

st.plotly_chart(fig_area, use_container_width=True)

# =====================================================
# PREDICTIVE ANALYTICS
# =====================================================

st.markdown("---")
st.markdown('<div id="forecast"></div>', unsafe_allow_html=True)

st.header("🔮 Predictive Analytics")

X = filtered_trends[['year']]
y = filtered_trends['total_patents']

model = LinearRegression()
model.fit(X, y)

future_years = np.arange(
    max_year + 1,
    max_year + 11
)

future_df = pd.DataFrame({
    'year': future_years
})

predictions = model.predict(future_df)

forecast_df = pd.DataFrame({
    'year': future_years,
    'predicted_patents': predictions
})

fig_forecast = go.Figure()

fig_forecast.add_trace(go.Scatter(
    x=filtered_trends['year'],
    y=filtered_trends['total_patents'],
    mode='lines+markers',
    name='Historical',
    line=dict(color="#00F5FF", width=4)
))

fig_forecast.add_trace(go.Scatter(
    x=forecast_df['year'],
    y=forecast_df['predicted_patents'],
    mode='lines+markers',
    name='Forecast',
    line=dict(color="#ff4fd8", width=4, dash="dash")
))

fig_forecast.update_layout(
    title="10-Year Patent Forecast",
    **PLOT_LAYOUT
)

st.plotly_chart(fig_forecast, use_container_width=True)

# =====================================================
# PRESCRIPTIVE ANALYTICS
# =====================================================

st.markdown("---")
st.markdown('<div id="recommend"></div>', unsafe_allow_html=True)

st.header("🧠 Prescriptive Analytics")

latest_prediction = int(
    forecast_df.iloc[-1]['predicted_patents']
)

if growth_rate > 50:

    st.success("""
    Patent activity is growing rapidly.
    Increase R&D investments and innovation partnerships.
    """)

elif growth_rate > 10:

    st.info("""
    Moderate growth detected.
    Focus on emerging technologies and strategic sectors.
    """)

else:

    st.warning("""
    Innovation growth is slowing.
    Increase research incentives and identify declining sectors.
    """)

st.metric(
    f"Projected Patents by {future_years[-1]}",
    f"{latest_prediction:,}"
)

# =====================================================
# RAW DATA
# =====================================================

st.markdown("---")
st.markdown('<div id="rawdata"></div>', unsafe_allow_html=True)

st.header("📁 Raw Data Explorer")

tab1, tab2, tab3 = st.tabs([
    "Inventors",
    "Companies",
    "Trends"
])

with tab1:
    st.dataframe(top_inventors, use_container_width=True)

with tab2:
    st.dataframe(top_companies, use_container_width=True)

with tab3:
    st.dataframe(filtered_trends, use_container_width=True)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "Patent Analytics Platform • Powered by PatentsView"
)