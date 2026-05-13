#Clde version updates with gemini

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
import logging
from data import GENRE_METRICS, SOUTH_INDIAN_ACTORS, DIRECTORS, SEASONAL_MULTIPLIERS
from formula import calculate_v3i_logic, calculate_detailed_prediction

# =====================================================
# SETUP & CONFIGURATION
# =====================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="v3i Cinema Predictor", layout="wide")

# API KEY SETUP
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY")
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

# =====================================================
# DATA FETCHING FUNCTIONS
# =====================================================

def search_movies_list(query):
    """Returns a list of potential movie matches using the 's' parameter."""
    if not OMDB_API_KEY:
        return []
    url = f"http://www.omdbapi.com/?s={query}&apikey={OMDB_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get("Search", []) if res.get("Response") == "True" else []
    except:
        return []

def fetch_detailed_data(imdb_id):
    """Fetches full details using a specific IMDb ID."""
    try:
        # 1. Exact details from OMDb
        omdb = requests.get(f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}").json()
        
        # 2. TMDB search using Title to get Credits/Budget
        title = omdb.get("Title")
        tmdb_search = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}").json()
        
        tmdb_data = {}
        if tmdb_search.get('results'):
            # Match by year if possible
            year = omdb.get("Year", "")[:4]
            match = next((m for m in tmdb_search['results'] if m.get('release_date', '').startswith(year)), tmdb_search['results'])
            m_id = match['id']
            tmdb_data = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={TMDB_API_KEY}&append_to_response=credits").json()
            
        return omdb, tmdb_data
    except:
        return None, None

# =====================================================
# UI LAYOUT
# =====================================================

st.title("South Indian Cinema Predictability Model v3i")

with st.sidebar:
    st.header("Step 1: Movie Search")
    search_query = st.text_input("Enter Title (e.g. Apex)", value="Apex")
    
    omdb, tmdb = None, None
    
    if search_query:
        search_results = search_movies_list(search_query)
        if search_results:
            # Create a dictionary for the selectbox: "Title (Year)" -> imdbID
            options = {f"{m['Title']} ({m['Year']})": m['imdbID'] for m in search_results}
            selected_label = st.selectbox("Step 2: Select the correct version", options.keys())
            
            # Fetch the final details based on selection
            if selected_label:
                omdb, tmdb = fetch_detailed_data(options[selected_label])
        else:
            st.warning("No results found for that title.")

    st.divider()
    
    # Pillar Inputs (Auto-populated if movie found)
    st.header("Step 3: Analyze Pillars")
    
    # Auto-mapping logic
    default_genre = "Action"
    if omdb:
        raw_genre = omdb.get("Genre", "Action").split(",").strip()
        default_genre = raw_genre if raw_genre in GENRE_METRICS else "Action"

    genre = st.selectbox("Genre", list(GENRE_METRICS.keys()), index=list(GENRE_METRICS.keys()).index(default_genre))
    
    actor_key = st.selectbox("Lead Actor", list(ACTORS.keys()))
    director_key = st.selectbox("Director", list(DIRECTORS.keys()))
    
    release_date = st.date_input("Release Date", value=date(2026, 1, 12))
    has_clash = st.checkbox("Superstar Clash?")
    
    # Budget safety
    tmdb_budget = (tmdb.get("budget", 0) / 10_000_000) if tmdb else 0
    budget = st.number_input("Budget (Crores)", value=float(tmdb_budget) if tmdb_budget > 0 else 100.0)

# =====================================================
# CALCULATION & DISPLAY
# =====================================================

if omdb:
    # Prepare inputs for the formula
    m_market = SEASONAL_MULTIPLIERS.get(release_date.month, 1.0)
    
    calc_inputs = {
        "talent_score": (SOUTH_INDIAN_ACTORS[actor_key]['score'] + DIRECTORS[director_key]['score']) / 2,
        "market_base": 85,
        "market_multiplier": m_market,
        "has_clash": has_clash,
        "content_score": GENRE_METRICS[genre]['base_score'],
        "viral_score": 75, # Default viral score
        "seasonal_score": 85 if m_market > 1.0 else 70,
        "m_cert": 1.0,
        "budget": budget if budget > 0 else 1.0
    }

    report = calculate_detailed_prediction(calc_inputs)

    # UI Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Predictability", f"{report['predictability_score']}%")
    c2.metric("Est. Revenue", f"₹{report['revenue_estimate']} Cr")
    c3.metric("ROI", f"{report['roi_percentage']}%")

    st.divider()
    
    # Metadata Display
    col_a, col_b = st.columns()
    with col_a:
        if omdb.get("Poster") != "N/A":
            st.image(omdb.get("Poster"))
    with col_b:
        st.subheader(f"{omdb.get('Title')} ({omdb.get('Year')})")
        st.write(f"**Synopsis:** {omdb.get('Plot')}")
        st.write(f"**Cast:** {omdb.get('Actors')}")
        st.info(f"Risk Level: {report['risk_level']}")