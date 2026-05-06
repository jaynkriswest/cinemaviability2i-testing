import streamlit as st
from formula import calculate_cinema_logic
from data import SOUTH_INDIAN_TALENT_DB, get_talent_weight

st.set_page_config(page_title="Cinema Predictor Pro", layout="wide")

st.title("Cinema Predictability AI (v5.0)")
st.markdown("---")

# Sidebar for Inputs
with st.sidebar:
    st.header("Project Parameters")
    actor = st.selectbox("Lead Actor", list(SOUTH_INDIAN_TALENT_DB.keys()))
    genre = st.selectbox("Genre", ["Action/Mass", "Drama", "Thriller", "Romance", "Comedy"])
    budget = st.number_input("Budget (in Crores)", min_value=1, value=50)
    festive_release = st.checkbox("Festive/Holiday Release?")

# Logic Mapping
talent_info = get_talent_weight(actor)
genre_weights = {"Action/Mass": 95, "Drama": 85, "Thriller": 80, "Romance": 75, "Comedy": 70}
season_mult = 1.2 if festive_release else 1.0

# Calculate using the Interaction Multiplier
final_score = calculate_cinema_logic(
    talent_score=talent_info["score"],
    genre_weight=genre_weights[genre],
    season_multiplier=season_mult,
    budget=budget,
    target_market=90 # Defaulting to high market reach for this example
)

# GUI Display
col1, col2 = st.columns(2)
with col1:
    st.metric("Success Probability", f"{final_score:.1f}%")
    if final_score > 85:
        st.success("Verdict: Blockbuster Potential")
    elif final_score > 70:
        st.info("Verdict: Safe Bet")
    else:
        st.warning("Verdict: High Risk")

with col2:
    st.subheader("Logic Breakdown")
    st.write(f"**Talent Category:** {talent_info['category']}")
    st.write(f"**Base Talent Weight:** {talent_info['score']}")
    if festive_release and talent_info['category'] == "Ultra-Veteran":
        st.write("*Mega-Synergy Multiplier Applied*")