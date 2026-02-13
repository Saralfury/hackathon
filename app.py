import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & TACTICAL CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NCT SURVEILLANCE // MAIN",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# INJECTING HIGH-END CSS
st.markdown("""
<style>
    /* IMPORT FUTURISTIC FONT */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');

    /* BACKGROUND THEME */
    .stApp {
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* REMOVE WHITESPACE */
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    
    /* CYBERPUNK CARD CONTAINER */
    .cyber-card {
        background: rgba(12, 12, 12, 0.7);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-left: 3px solid #00f0ff;
        border-radius: 2px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.05);
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    .cyber-card:hover {
        border-color: #00f0ff;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
        transform: translateX(5px);
    }
    
    /* METRIC TYPOGRAPHY */
    .cyber-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 5px;
    }
    .cyber-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #fff;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #020202;
        border-right: 1px solid #1a1a1a;
    }
    
    /* HEADER */
    h1 {
        color: #fff;
        text-transform: uppercase;
        letter-spacing: 3px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA ENGINE
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        # Robust loading: Check local first, then subfolder
        try:
            df = pd.read_csv("crime_data.csv")
        except FileNotFoundError:
            df = pd.read_csv("crime-dashboard/crime_data.csv")
            
        # Processing
        df['date'] = pd.to_datetime(df['date'])
        df['hour'] = df['date'].dt.hour
        
        # --- THE FIX IS HERE ---
        # Convert date objects to string to prevent JSON serialization error
        df['day'] = df['date'].dt.date.astype(str) 
        
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM PARAMETERS")
    st.markdown("---")
    
    if not df.empty:
        # Date Filter
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        dates = st.date_input("TEMPORAL WINDOW", [min_date, max_date], min_value=min_date, max_value=max_date)
        
        # Multiselects
        zones = st.multiselect("SECTORS", df['zone'].unique(), default=df['zone'].unique())
        crimes = st.multiselect("OFFENSE CODES", df['crime_type'].unique(), default=df['crime_type'].unique())
        
        # Apply Filters
        # Handle single date vs range tuple
        if isinstance(dates, tuple):
            if len(dates) == 2:
                start_d, end_d = dates
                mask = (df['day'] >= str(start_d)) & (df['day'] <= str(end_d))
            elif len(dates) == 1:
                mask = (df['day'] == str(dates[0]))
            else:
                mask = [True] * len(df)
        else:
            mask = (df['day'] == str(dates))
            
        mask &= df['zone'].isin(zones)
        mask &= df['crime_type'].isin(crimes)
        filtered_df = df.loc[mask]
    else:
        filtered_df = pd.DataFrame()

# -----------------------------------------------------------------------------
# 4. HEADER & KPI GRID
# -----------------------------------------------------------------------------
st.markdown("<h1>NCT SURVEILLANCE GRID <span style='font-size:1rem; color:#00f0ff; vertical-align:middle; float:right;'>● LIVE FEED</span></h1>", unsafe_allow_html=True)

if filtered_df.empty:
    st.error("SYSTEM OFFLINE: NO DATA FOUND. CHECK CONNECTION.")
    st.stop()

# KPIs
k1, k2, k3, k4 = st.columns(4)

total = len(filtered_df)
risk_zone = filtered_df['zone'].mode()[0]
primary_code = filtered_df['crime_type'].mode()[0]
peak_h = f"{filtered_df['hour'].mode()[0]}:00"

def kpi_card(label, value):
    return f"""
    <div class="cyber-card">
        <div class="cyber-label">{label}</div>
        <div class="cyber-value">{value}</div>
    </div>
    """

k1.markdown(kpi_card("TOTAL INCIDENTS", f"{total:,}"), unsafe_allow_html=True)
k2.markdown(kpi_card("HIGH RISK SECTOR", risk_zone), unsafe_allow_html=True)
k3.markdown(kpi_card("PRIMARY OFFENSE", primary_code), unsafe_allow_html=True)
k4.markdown(kpi_card("PEAK ACTIVITY", peak_h), unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. MAIN COMMAND INTERFACE
# -----------------------------------------------------------------------------
col_3d, col_analytics = st.columns([0.65, 0.35])

with col_3d:
    st.markdown("**🌐 3D GEOSPATIAL EXTRUSION**")
    
    # 3D MAP CONFIGURATION (DECK.GL)
    layer = pdk.Layer(
        "HexagonLayer",
        data=filtered_df,
        get_position=["longitude", "latitude"],
        radius=200,                # Radius of bin
        elevation_scale=5,         # Height of bars
        elevation_range=[0, 100],
        extruded=True,
        pickable=True,
        # Neon Gradient: Purple to Cyan
        get_fill_color="[255 * (1 - count / 50), 100, 255, 200]", 
    )

    view_state = pdk.ViewState(
        latitude=28.6139,
        longitude=77.2090,
        zoom=10,
        pitch=55,       # Tilted View
        bearing=-25     # Rotated View
    )

    # Dark Map Style
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        # Use this style which requires NO API Token
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json", 
        tooltip={"html": "<b>Density:</b> {elevationValue}", "style": {"backgroundColor": "#111", "color": "#00f0ff"}}
    )
    
    st.pydeck_chart(deck)

with col_analytics:
    st.markdown("**� TACTICAL BREAKDOWN**")
    
    # 1. Neon Bar Chart
    counts = filtered_df['crime_type'].value_counts().reset_index()
    counts.columns = ['Type', 'Count']
    
    fig_bar = px.bar(counts, x='Count', y='Type', orientation='h', template="plotly_dark")
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rajdhani", color="#00f0ff"),
        margin=dict(l=0, r=0, t=0, b=0),
        height=250,
        yaxis=dict(autorange="reversed") # Highest on top
    )
    fig_bar.update_traces(marker_color='#00f0ff', marker_line_color='#fff', marker_line_width=1)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # 2. Neon Area Trend
    trend = filtered_df.groupby('date').size().reset_index(name='Count')
    fig_trend = px.area(trend, x='date', y='Count', template="plotly_dark")
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rajdhani", color="#888"),
        margin=dict(l=0, r=0, t=20, b=0),
        height=200,
        xaxis_title=None,
        yaxis_title=None
    )
    fig_trend.update_traces(line_color='#bf00ff', fillcolor='rgba(191, 0, 255, 0.2)')
    st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. DATA FEED (FOOTER)
# -----------------------------------------------------------------------------
with st.expander("📂 DECLASSIFIED DATA LOGS", expanded=False):
    st.dataframe(
        filtered_df[['date', 'hour', 'zone', 'crime_type', 'latitude', 'longitude']].sort_values('date', ascending=False),
        use_container_width=True,
        height=300
    )
