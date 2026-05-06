import streamlit as st
from datetime import date
from data import TALENT_DATABASE, GENRE_METRICS
from formula import calculate_v3i_logic

st.set_page_config(page_title="Cinema Predictor v3i", layout="wide")
st.title("South Indian Cinema Predictability Model v3i")

with st.sidebar:
    st.header("Pillar 1: Talent & Credits")
    actor_name = st.selectbox("Lead Actor / Director", list(TALENT_DATABASE.keys()))
    t_data = TALENT_DATABASE[actor_name]
    st.caption(f"Tier: {t_data['tier']} | Logic: {t_data['criteria']}")

    st.header("Pillar 2 & 3: Market & Date")
    release_date = st.date_input("Release Date", value=date(2026, 1, 14))
    has_clash = st.checkbox("Major Superstar Clash? (-0.15 Penalty)")
    
    st.header("Pillar 4: Viral Momentum")
    # Based on YouTube/Social Velocity defined in v3i_3.docx
    viral_tier = st.select_slider(
        "Trailer/Music Hype",
        options=["Low", "Moderate", "High"],
        value="Moderate"
    )
    viral_map = {"Low": 40, "Moderate": 70, "High": 95}

    st.header("Pillar 5: Content & Reach")
    genre = st.selectbox("Genre", list(GENRE_METRICS.keys()))
    is_franchise = st.checkbox("Franchise / Sequel Bonus (1.4x)")
    cert = st.selectbox("Certification (M_Cert)", ["U", "UA", "A"])
    is_aligned = st.checkbox("Marketing matches Film Tone?", value=True)

    st.header("Financials")
    budget = st.number_input("Budget (Crores)", min_value=5, max_value=1000, value=100)

# Multiplier Logic based on v3i_3.docx
m_cert = {"U": 1.2, "UA": 1.0, "A": 0.7}[cert]
m_align = 1.0 if is_aligned else 0.9

# Date-based Market Multiplier
m_market = 1.0
if release_date.month == 1 and 13 <= release_date.day <= 17:
    m_market = 1.3  # Sankranti/Pongal
elif 4 <= release_date.month <= 6:
    m_market = 1.15 # Summer Vacation

# Bundle inputs for Formula
inputs = {
    "talent_score": t_data['score'],
    "market_base": 80,         
    "market_multiplier": m_market,
    "has_clash": has_clash,
    "content_score": GENRE_METRICS[genre]['base_score'],
    "viral_score": viral_map[viral_tier],
    "seasonal_score": 85 if m_market > 1.0 else 70,
    "m_cert": m_cert,
    "m_align": m_align,
    "budget": budget,
    "is_franchise": is_franchise
}

prob, revenue, roi = calculate_v3i_logic(inputs)

# Results Dashboard
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Predictability Score", f"{prob:.1f}%")
with col2:
    st.metric("Est. Gross Revenue", f"₹{revenue:.1f} Cr")
with col3:
    st.metric("Projected ROI", f"{roi:.1f}%", delta=f"{roi:.1f}%")

st.divider()
st.subheader("Technical Analysis")
st.write(f"This project utilizes the **{t_data['tier']}** stability floor.")
st.write(f"The Genre baseline for **{genre}** is factored as **{GENRE_METRICS[genre]['risk']}**.")