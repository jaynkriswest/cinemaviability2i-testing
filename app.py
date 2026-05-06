# app.py
import streamlit as st
from data import SOUTH_INDIAN_TALENT_DB, GENRE_BASELINES, get_talent_weight
from formula import calculate_v3i_logic

st.title("Cinema Predictability")

with st.sidebar:
    st.header("1. Talent & Content")
    actor = st.selectbox("Lead Actor", list(SOUTH_INDIAN_TALENT_DB.keys()))
    genre = st.selectbox("Genre", list(GENRE_BASELINES.keys()))
    is_franchise = st.checkbox("IP / Franchise Sequel? (1.4x Bonus)")
    
    st.header("2. Market & Season")
    window = st.selectbox("Release Window", ["Sankranti", "Summer", "Monsoon", "Normal"])
    clash = st.checkbox("Major Superstar Clash? (-0.15 Penalty)")
    
    st.header("3. Distribution & Reach")
    cert = st.selectbox("Certification", ["U", "UA", "A"])
    m_cert = {"U": 1.2, "UA": 1.0, "A": 0.7}[cert]

# Mapping Seasonal/Market scores from v3i document
market_scores = {"Sankranti": 100, "Summer": 90, "Monsoon": 75, "Normal": 70}
s_market = market_scores[window] - (15 if clash else 0) # Apply Clash Penalty]

# Execute Logic
results = {
    "talent_score": get_talent_weight(actor)["score"],
    "market_score": s_market,
    "content_score": GENRE_BASELINES[genre],
    "viral_score": 85, # Defaulting for now
    "seasonal_score": 90 if window != "Normal" else 70,
    "m_cert": m_cert,
    "m_align": 1.0,
    "budget": 100,
    "is_franchise": is_franchise
}

prob, roi = calculate_v3i_logic(results)

# Display Results
st.metric("Predictability Score", f"{prob:.1f}%")
st.metric("Projected ROI", f"{roi:.1f}%")