# Updated from Main folder updated from testing (Claudegem1i)

# app.py - Production Layout and Argument Synchronizer

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(
    page_title="Cinema Intelligence Platform",
    layout="wide"
)

TMDB_API_KEY = (
    st.secrets.get("TMDB_API_KEY")
    or os.getenv("TMDB_API_KEY")
)

if not TMDB_API_KEY:
    st.error("Missing TMDB_API_KEY. Please specify this parameter in your environment config.")
    st.stop()

# DATA MODULE IMPORT CONSTRAINTS
try:
    from data import (
        GENRE_METRICS,
        SOUTH_INDIAN_ACTORS,
        DIRECTORS,
        SEASONAL_MULTIPLIERS,
    )
    from formula import calculate_detailed_prediction
    from movie_insights import (
        search_movies_by_synopsis,
        fetch_full_movie_details,
        classify_movie_success,
        analyze_success_reasons,
        analyze_failure_reasons,
    )
except ImportError as e:
    st.error(f"Required structural subsystem reference loading failed: {e}")
    st.stop()

# =====================================================
# DISPLAY MAPPING COMPILATIONS
# =====================================================

ACTOR_DISPLAY_MAP = {
    "Chirankeevi": "chiranjeevi",
    "Kamal Haasan": "kamal_haasan",
    "Rajinikanth": "rajinikanth",
}

DIRECTOR_DISPLAY_MAP = {
    "S.S. Rajamouli": "rajamouli",
    "Sukumar": "sukumar",
    "Lokesh Kanagaraj": "lokesh_kanagaraj",
    "Trivikram Srinivas": "trivikram_srinivas",
}

GENRE_DISPLAY_MAP = {
    "Action": "Action",
    "Drama": "Drama",
    "Thriller": "Thriller",
    "Comedy": "Comedy",
    "Romance": "Romance",
}

# =====================================================
# LAYOUT STRUCTURE
# =====================================================

st.title("South Indian Cinema Predictability Model v5")
st.divider()

prediction_col, search_col = st.columns([1.2, 1])

# =====================================================
# LEFT PANEL: PREDICTABILITY ENGINE
# =====================================================

with prediction_col:
    st.header("Predictability Model Engine")
    
    actor_label = st.selectbox("Lead Actor Profile", options=list(ACTOR_DISPLAY_MAP.keys()))
    director_label = st.selectbox("Director Profile", options=list(DIRECTOR_DISPLAY_MAP.keys()))
    genre_label = st.selectbox("Primary Genre Definition", options=list(GENRE_DISPLAY_MAP.keys()))
    
    budget = st.number_input("Budget Exposure Ceiling (INR Crores)", min_value=1.0, max_value=600.0, value=150.0, step=10.0)
    release_date = st.date_input("Target Release Schedule Date", value=date(2026, 1, 1))
    
    has_clash = st.checkbox("Holiday Release Clashes")
    is_franchise = st.checkbox("Franchise / IP Sequel")
    
    censor_rating = st.radio("Censor Allocation", options=["U", "UA", "A"], index=1)
    viral_hype = st.select_slider("Promotional Viral Traction", options=["Low", "Moderate", "High"], value="Moderate")
    marketing_alignment = st.slider("Marketing Consistency", min_value=0.8, max_value=1.0, value=0.95, step=0.01)

    future_synopsis_text = st.text_area("Future Script Synopsis", value="A dynamic protagonist works within an underground network...")

    if st.button("Run Analytics Engine Pipeline", type="primary", use_container_width=True):
        actor_score = SOUTH_INDIAN_ACTORS[ACTOR_DISPLAY_MAP[actor_label]]["score"]
        director_score = DIRECTORS[DIRECTOR_DISPLAY_MAP[director_label]]["score"]
        
        inputs = {
            "talent_score": (actor_score * 0.6) + (director_score * 0.4),
            "content_score": GENRE_METRICS[GENRE_DISPLAY_MAP[genre_label]]["base_score"],
            "viral_score": {"Low": 50, "Moderate": 70, "High": 90}[viral_hype],
            "m_cert": {"U": 1.2, "UA": 1.0, "A": 0.7}[censor_rating],
            "budget": budget, "has_clash": has_clash, "is_franchise": is_franchise,
            "m_align": marketing_alignment
        }
        
        pred = calculate_detailed_prediction(inputs)
        st.subheader("Engine Valuation Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Predictability", f"{pred['predictability_score']:.1f}%")
        m2.metric("Gross Revenue", f"₹{pred['revenue_estimate']:.1f} Cr")
        m3.metric("ROI Yield", f"{pred['roi_percentage']:.1f}%")

# =====================================================
# RIGHT PANEL: TITLE SEARCH ENGINE
# =====================================================

with search_col:
    st.header("Historical Narrative Benchmarking")
    query = st.text_input("Search Regional Reference Title", key="right_panel_title_query")
    
    # Use a container to ensure results clear/refresh correctly
    results_container = st.container()

    if query:
        historical_pool = search_movies_by_title_raw_internal(query)
        if historical_pool:
            options = {f"{m.get('title')} ({m.get('release_date', '####')[:4]})": m.get('id') for m in historical_pool}
            selected_label = st.selectbox("Resolve Match", options=list(options.keys()))
            
            if selected_label:
                movie_details = fetch_full_movie_details(options[selected_label], TMDB_API_KEY)
                with results_container:
                    if movie_details:
                        # FIXED: Added weights to st.columns
                        card_left, card_right = st.columns()
                        with card_left:
                            if movie_details.get("poster_path"):
                                st.image(f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}", use_container_width=True)
                        with card_right:
                            st.subheader(f"{movie_details.get('title')}")
                            st.write(f"**Genre:** {', '.join([g['name'] for g in movie_details.get('genres', [])])}")
                            st.write(f"**Cast:** {movie_details.get('extracted_cast', 'N/A')}")
                        st.write(movie_details.get("overview", "No plot summary."))
                        st.subheader("Similar Historical Films")
                        for rec in movie_details.get("extracted_recommendations", []):
                            st.markdown(f"• {rec.get('title')}")

def search_movies_by_title_raw_internal(title_query):
    try:
        res = requests.get("https://api.themoviedb.org/3/search/movie", 
                           params={"api_key": TMDB_API_KEY, "query": title_query, "region": "IN"}, timeout=5)
        return res.json().get("results", [])[:5]
    except: return []

# FOOTER ARCHITECTURE
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85em;">
    <p>Cinema Predictability Model v5 | Powered by OMDB/TMDB APIs</p>
</div>
""", unsafe_allow_html=True)