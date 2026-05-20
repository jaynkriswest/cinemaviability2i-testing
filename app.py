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
st.set_page_config(page_title="Cinema Intelligence Platform", layout="wide")

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    st.error("Missing TMDB_API_KEY. Please specify this parameter in your environment config.")
    st.stop()

# --- HELPER FUNCTIONS (Defined BEFORE usage) ---
def search_movies_by_title_raw_internal(title_query):
    try:
        res = requests.get("https://api.themoviedb.org/3/search/movie", 
                           params={"api_key": TMDB_API_KEY, "query": title_query, "region": "IN"}, timeout=5)
        return res.json().get("results", [])[:5]
    except: return []

# DATA MODULE IMPORT CONSTRAINTS
try:
    from data import GENRE_METRICS, SOUTH_INDIAN_ACTORS, DIRECTORS, SEASONAL_MULTIPLIERS
    from formula import calculate_detailed_prediction
    from movie_insights import (
        search_movies_by_synopsis, fetch_full_movie_details,
        analyze_success_reasons, analyze_failure_reasons
    )
except ImportError as e:
    st.error(f"Required structural subsystem reference loading failed: {e}")
    st.stop()

# =====================================================
# LAYOUT STRUCTURE
# =====================================================

st.title("South Indian Cinema Predictability Model v5")
st.divider()

prediction_col, search_col = st.columns([1.2, 1])

# =====================================================
# LEFT PANEL
# =====================================================
with prediction_col:
    st.header("Predictability Model Engine")
    # ... [Keep your existing UI logic here] ...
    if st.button("Run Analytics Engine Pipeline", type="primary", use_container_width=True):
        # ... [Your calculation logic] ...
        st.subheader("Engine Valuation Metrics")
        # Ensure your tab rendering code is placed here

# =====================================================
# RIGHT PANEL
# =====================================================
with search_col:
    st.header("Historical Narrative Benchmarking")
    query = st.text_input("Search Regional Reference Title", key="right_panel_title_query")
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
                        # FIXED: Added weight to prevent TypeError
                        card_left, card_right = st.columns(2) 
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

# FOOTER
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85em;">
    <p>Cinema Predictability Model v5 | Powered by OMDB/TMDB APIs</p>
</div>
""", unsafe_allow_html=True)