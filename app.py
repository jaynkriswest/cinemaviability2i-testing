import streamlit as st
from datetime import date, timedelta
from data import SOUTH_INDIAN_TALENT_DB, GENRE_BASELINES
from formula import calculate_v3i_logic

st.set_page_config(page_title="Cinema Predictor v3i", layout="wide")
st.title("🎬 Cinema Predictor: Future-Dated Analysis")

with st.sidebar:
    st.header("Project Parameters")
    actor_name = st.selectbox("Lead Actor", list(SOUTH_INDIAN_TALENT_DB.keys()))
    genre = st.selectbox("Genre", list(GENRE_BASELINES.keys()))
    budget = st.slider("Production Budget (Cr)", 10, 600, 100)
    
    st.header("Strategic Planning")
    # EXTENDED DATE RANGE: Allows picking any date from today up to 2030
    release_date = st.date_input(
        "Select Release Date", 
        value=date.today(),
        min_value=date.today(),
        max_value=date(2030, 12, 31)
    )
    has_clash = st.checkbox("Is there a major clash?")
    cert = st.selectbox("Certification", ["U", "UA", "A"])
    is_franchise = st.checkbox("Franchise/IP Bonus")

# Execute Logic
actor_data = SOUTH_INDIAN_TALENT_DB[actor_name]
m_cert = {"U": 1.2, "UA": 1.0, "A": 0.7}[cert]

inputs = {
    "talent_score": actor_data['score'],
    "content_score": GENRE_BASELINES[genre],
    "release_date": release_date,
    "has_clash": has_clash,
    "viral_score": 85,
    "m_cert": m_cert,
    "m_align": 1.0,
    "budget": budget,
    "is_franchise": is_franchise
}

prob, rev, roi = calculate_v3i_logic(inputs)

# UI Display
st.metric("Success Predictability", f"{prob:.1f}%")
st.metric("Estimated Revenue", f"₹{rev:.1f} Cr")
st.metric("ROI", f"{roi:.1f}%")

if roi < 0:
    st.error(f"⚠️ High Risk: A release on {release_date.year} for this budget-talent mix is not currently viable.")