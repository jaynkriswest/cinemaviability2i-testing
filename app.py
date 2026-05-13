import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
from data import GENRE_METRICS
from formula import calculate_v3i_logic

# 1. SETUP & SECURITY
load_dotenv()

# Prioritize Streamlit Secrets for cloud deployment, fallback to .env for local
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY")
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

st.set_page_config(page_title="Real-Time Predictor v3i", layout="wide")
st.title("South Indian Cinema Predictability Model v3ss")

# 2. DATA FETCHING FUNCTION
def fetch_movie_metadata(title):
    if not OMDB_API_KEY or not TMDB_API_KEY:
        return None, None
    
    try:
        # Fetch from OMDb
        omdb_res = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}").json()
        
        # Fetch from TMDB for Credits & Budget
        tmdb_search = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}").json()
        
        tmdb_details = {}
        if tmdb_search.get('results') and len(tmdb_search['results']) > 0:
            # FIX: Added to get the ID from the first search result
            movie_id = tmdb_search['results']['id']
            tmdb_details = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits").json()
        
        return omdb_res, tmdb_details
    except Exception:
        return None, None

# 3. SIDEBAR INPUTS
with st.sidebar:
    st.header("Real-Time Search")
    search_query = st.text_input("Enter Movie Title", value="Mana Shankara Varaprasad Garu")
    
    omdb, tmdb = None, None
    if search_query:
        omdb, tmdb = fetch_movie_metadata(search_query)

    st.divider()
    
    if omdb and omdb.get("Response") == "True":
        st.success(f"Linked to: {omdb['Title']}")
        # Map Certification
        cert_val = omdb.get("Rated", "UA")
        m_cert = {"U": 1.2, "UA": 1.0, "U/A": 1.0, "A": 0.7}.get(cert_val, 1.0)
        
        # FIX: Added before .strip() to clean the first genre string
        raw_genre = omdb.get("Genre", "Action")
        first_genre = raw_genre.split(",").strip()
        genre = first_genre if first_genre in GENRE_METRICS else "Action"
        
        # Map Budget (Convert TMDB value to Crores)
        tmdb_val = tmdb.get("budget", 0)
        budget = st.number_input("Budget (Crores)", value=float(tmdb_val / 10000000) if tmdb_val > 0 else 200.0)
    else:
        st.warning("Manual fallback active.")
        m_cert = 1.0
        genre = "Action"
        budget = st.number_input("Budget (Crores)", value=200.0)

    st.header("Pillar 1: Talent")
    talent_tier = st.selectbox("Assign Talent Tier", ["Ultra-Veteran", "Veteran", "Superstar", "Rising Star"])
    talent_map = {"Ultra-Veteran": 98, "Veteran": 90, "Superstar": 92, "Rising Star": 70}
    
    st.header("Pillar 2 & 4: Market & Viral")
    release_date = st.date_input("Release Date", value=date(2026, 1, 12))
    has_clash = st.checkbox("Major Superstar Clash?")
    viral_tier = st.select_slider("Viral Hype", options=["Low", "Moderate", "High"], value="Moderate")
    viral_map = {"Low": 40, "Moderate": 70, "High": 95}

# 4. LOGIC PROCESSING
m_market = 1.3 if (release_date.month == 1 and 12 <= release_date.day <= 17) else (1.15 if 4 <= release_date.month <= 6 else 1.0)

inputs = {
    "talent_score": talent_map[talent_tier],
    "market_base": 85,
    "market_multiplier": m_market,
    "has_clash": has_clash,
    "content_score": GENRE_METRICS[genre]['base_score'],
    "viral_score": viral_map[viral_tier],
    "seasonal_score": 85 if m_market > 1.0 else 70,
    "m_cert": m_cert,
    "m_align": 1.0,
    "budget": budget,
    "is_franchise": False 
}

prob, revenue, roi = calculate_v3i_logic(inputs)

# 5. UI DISPLAY
col1, col2, col3 = st.columns(3)
with col1: st.metric("Predictability Score", f"{prob:.1f}%")
with col2: st.metric("Est. Gross Revenue", f"₹{revenue:.1f} Cr")
with col3: st.metric("Projected ROI", f"{roi:.1f}%")

if omdb:
    st.divider()
    st.subheader("Technical Analysis Data (IMDb)")
    st.write(f"**Synopsis:** {omdb.get('Plot')}")
    # Display Actors and Genre metadata
    st.write(f"**Cast:** {omdb.get('Actors')}")
    st.write(f"**Genre:** {omdb.get('Genre')} | **Certification:** {omdb.get('Rated')}")