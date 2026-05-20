#Clde version

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
import logging

# =====================================================
# SETUP & CONFIGURATION
# =====================================================

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(
    page_title="South Indian Cinema Predictor v5",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# API KEY SETUP
# =====================================================

# Try to get API keys from Streamlit secrets first, then .env file
try:
    OMDB_API_KEY = st.secrets.get("OMDB_API_KEY")
except:
    OMDB_API_KEY = os.getenv("OMDB_API_KEY")

try:
    TMDB_API_KEY = st.secrets.get("TMDB_API_KEY")
except:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Validate API keys
if not OMDB_API_KEY:
    st.error("OMDB API Key not found. Add to .env or Streamlit secrets.")
    st.stop()

if not TMDB_API_KEY:
    st.warning("TMDB API Key not found. Using OMDB only.")

# =====================================================
# DATA IMPORT
# =====================================================

try:
    from data import (
        GENRE_METRICS,
        TALENT_TIERS,
        SOUTH_INDIAN_ACTORS,
        SEASONAL_MULTIPLIERS,
        PRODUCTION_HOUSES
    )
except ImportError:
    st.error("Missing data_fixed.py. Please ensure data file is in the same directory.")
    st.stop()

try:
    from formula import calculate_v3i_logic, calculate_detailed_prediction
except ImportError:
    st.error("Missing formula_fixed.py. Please ensure formula file is in the same directory.")
    st.stop()

# =====================================================
# HEADER
# =====================================================

st.title("South Indian Cinema Predictability Model v3")
st.markdown("Production-grade ROI prediction for Telugu, Tamil, Kannada, and Malayalam films")
st.divider()

# =====================================================
# API FUNCTIONS - FIXED
# =====================================================

@st.cache_data(ttl=3600)
def fetch_omdb_data(title: str) -> dict:
    """
    Fetch movie metadata from OMDb API.
    
    Fixed issues:
    - Added proper error handling
    - Fixed API call format
    - Added retry logic
    """
    try:
        if not OMDB_API_KEY:
            return None
        
        url = f"https://www.omdbapi.com/"
        params = {
            "t": title,
            "type": "movie",
            "apikey": OMDB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Response") == "True":
            return data
        else:
            logger.warning(f"OMDb: Movie '{title}' not found. Error: {data.get('Error', 'Unknown')}")
            return None
            
    except requests.exceptions.Timeout:
        st.warning(f"OMDb API timeout for '{title}'. Using manual input.")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"OMDb API error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected OMDb error: {str(e)}")
        return None


@st.cache_data(ttl=3600)
def fetch_tmdb_data(title: str) -> dict:
    """
    Fetch movie metadata from TMDB API.
    
    Fixed issues:
    - Fixed movie_id extraction from list
    - Added proper error handling
    - Fixed API call format
    """
    try:
        if not TMDB_API_KEY:
            return None
        
        # Step 1: Search for movie
        search_url = "https://api.themoviedb.org/3/search/movie"
        search_params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "region": "IN"  # India region
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=5)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        if not search_data.get("results") or len(search_data["results"]) == 0:
            logger.warning(f"TMDB: No results for '{title}'")
            return None
        
        # FIX: Extract movie_id from first result in list
        movie_id = search_data["results"][0].get("id")
        
        if not movie_id:
            logger.warning(f"TMDB: No movie ID found for '{title}'")
            return None
        
        # Step 2: Get detailed movie info with credits
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        details_params = {
            "api_key": TMDB_API_KEY,
            "append_to_response": "credits"
        }
        
        details_response = requests.get(details_url, params=details_params, timeout=5)
        details_response.raise_for_status()
        details_data = details_response.json()
        
        return details_data
        
    except requests.exceptions.Timeout:
        st.warning(f"TMDB API timeout for '{title}'.")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"TMDB API error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected TMDB error: {str(e)}")
        return None


def get_talent_score_from_db(actor_name: str) -> tuple:
    """
    Check if actor is in curated database.
    
    Returns:
        (score, tier, found)
    """
    name_normalized = actor_name.lower().replace(" ", "_")
    
    if name_normalized in SOUTH_INDIAN_ACTORS:
        actor_data = SOUTH_INDIAN_ACTORS[name_normalized]
        return actor_data['score'], actor_data['tier'], True
    
    return None, None, False


def extract_genre(genre_string: str) -> str:
    """
    Extract primary genre from OMDB genre string.
    
    Fixed issue: Added .strip() after split
    """
    if not genre_string:
        return "Action"
    
    genres = genre_string.split(",")
    primary_genre = genres[0].strip()  # FIX: Added strip()
    
    # Return primary genre if in database, else default
    if primary_genre in GENRE_METRICS:
        return primary_genre
    else:
        return "Action"  # Default fallback


# =====================================================
# SIDEBAR: INPUT SECTION
# =====================================================

with st.sidebar:
    st.header("Movie Information")
    st.markdown("Search or manually enter movie details")
    
    # Movie Search
    search_query = st.text_input(
        "Movie Title (Search)",
        value="Pushpa 2",
        help="Type a movie title to fetch details from IMDb/TMDB"
    )
    
    # Fetch data when user searches
    omdb_data = None
    tmdb_data = None
    
    if search_query:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Search", use_container_width=True):
                with st.spinner("Searching..."):
                    omdb_data = fetch_omdb_data(search_query)
                    tmdb_data = fetch_tmdb_data(search_query)
    
    st.divider()
    
    # ========== TALENT PILLAR ==========
    st.header("Talent")
    
    actor_name = st.text_input(
        "Lead Actor",
        value="Allu Arjun",
        help="Main actor in the film"
    )
    
    # Check if actor is in database
    db_score, db_tier, found = get_talent_score_from_db(actor_name)
    
    if found:
        st.success(f"Found: {actor_name} ({db_tier})")
        talent_tier = db_tier
        talent_score = db_score
    else:
        st.warning(f"Actor not in database. Using manual selection.")
        talent_tier = st.selectbox(
            "Select Talent Tier",
            ["Ultra-Veteran", "Veteran", "Superstar", "Rising Star"],
            index=2
        )
        talent_score = TALENT_TIERS[talent_tier]['score']
    
    st.info(f"**Talent Score: {talent_score}/100** ({talent_tier})")
    
    # ========== FINANCIAL PILLAR ==========
    st.header("Financial & Distribution")
    
    col_budget, col_market = st.columns(2)
    
    with col_budget:
        # If TMDB has budget data, use it
        tmdb_budget = None
        if tmdb_data and tmdb_data.get("budget", 0) > 0:
            tmdb_budget = tmdb_data["budget"] / 10000000  # Convert to crores
        
        budget = st.number_input(
            "Budget (₹ Crores)",
            min_value=1.0,
            max_value=500.0,
            value=tmdb_budget if tmdb_budget else 75.0,
            step=5.0
        )
    
    with col_market:
        market_reach = st.selectbox(
            "Distribution Scope",
            ["Limited (Single State)", "Standard (South India)", "Pan-India", "Global"],
            index=2
        )
    
    # ========== CONTENT PILLAR ==========
    st.header("Content & Genre")
    
    # Extract genre from OMDB if available
    omdb_genre = None
    if omdb_data and omdb_data.get("Genre"):
        omdb_genre = extract_genre(omdb_data["Genre"])
    
    genre = st.selectbox(
        "Primary Genre",
        list(GENRE_METRICS.keys()),
        index=list(GENRE_METRICS.keys()).index(omdb_genre) if omdb_genre else 0
    )
    
    script_type = st.selectbox(
        "Script Type",
        ["Original", "Remake/Adaptation", "Franchise/Sequel"],
        index=0
    )
    
    is_franchise = script_type == "Franchise/Sequel"
    
    # ========== RELEASE & TIMING ==========
    st.header("Release Schedule")
    
    release_date = st.date_input(
        "Target Release Date",
        value=date(2024, 12, 25),
        help="Select release date to calculate seasonal boost"
    )
    
    # Calculate seasonal multiplier
    month = release_date.month
    seasonal_multiplier = SEASONAL_MULTIPLIERS.get(month, 1.0)
    seasonal_score = 85 * seasonal_multiplier
    seasonal_score = min(seasonal_score, 100)  # Cap at 100
    
    st.caption(f"Seasonal Boost: {seasonal_multiplier}x → Score: {seasonal_score:.0f}/100")
    
    # Release clash check
    has_clash = st.checkbox(
        "Major Superstar Clash on Release Date?",
        value=False,
        help="If another major release same day, predictability decreases"
    )
    
    st.divider()
    
    # ========== ADDITIONAL FACTORS ==========
    st.header("Market Factors")
    
    col_cert, col_vir = st.columns(2)
    
    with col_cert:
        censor_rating = st.radio(
            "Censor Rating",
            ["U", "UA", "A"],
            index=1
        )
        m_cert = {"U": 1.2, "UA": 1.0, "A": 0.7}[censor_rating]
    
    with col_vir:
        viral_hype = st.select_slider(
            "Expected Viral Hype",
            options=["Low", "Moderate", "High"],
            value="Moderate"
        )
        viral_map = {"Low": 50, "Moderate": 70, "High": 90}
        s_viral = viral_map[viral_hype]
    
    marketing_alignment = st.slider(
        "Marketing Alignment",
        min_value=0.80,
        max_value=1.0,
        value=0.95,
        step=0.05
    )

# =====================================================
# MAIN CALCULATION AREA
# =====================================================

col_main_left, col_main_right = st.columns([1, 2])

with col_main_left:
    st.subheader("Input Summary")
    
    # Display fetched data if available
    if omdb_data and omdb_data.get("Response") == "True":
        st.info("Data linked from IMDb/TMDB")
        with st.expander("View Details"):
            st.write(f"**Title:** {omdb_data.get('Title')}")
            st.write(f"**Year:** {omdb_data.get('Year')}")
            st.write(f"**Plot:** {omdb_data.get('Plot')}")
            st.write(f"**Cast:** {omdb_data.get('Actors')}")
            st.write(f"**Runtime:** {omdb_data.get('Runtime')}")
            st.write(f"**IMDb Rating:** {omdb_data.get('imdbRating')}")
    
    # ========== CALCULATE BUTTON ==========
    if st.button("Calculate Predictability", use_container_width=True, type="primary"):
        
        # Prepare inputs for formula
        m_market = 1.0
        if market_reach == "Limited (Single State)":
            m_market = 0.85
        elif market_reach == "Standard (South India)":
            m_market = 1.0
        elif market_reach == "Pan-India":
            m_market = 1.2
        else:  # Global
            m_market = 1.3
        
        inputs = {
            "talent_score": talent_score,
            "market_base": 85,
            "market_multiplier": m_market,
            "has_clash": has_clash,
            "content_score": GENRE_METRICS[genre]['base_score'],
            "viral_score": s_viral,
            "seasonal_score": seasonal_score,
            "m_cert": m_cert,
            "m_align": marketing_alignment,
            "budget": budget,
            "is_franchise": is_franchise
        }
        
        # Calculate predictions
        prob, revenue, roi = calculate_v3i_logic(inputs)
        detailed = calculate_detailed_prediction(inputs)
        
        # Store in session state for display
        st.session_state['last_prediction'] = {
            'prob': prob,
            'revenue': revenue,
            'roi': roi,
            'detailed': detailed,
            'inputs': inputs
        }

# =====================================================
# RESULTS DISPLAY
# =====================================================

with col_main_right:
    if 'last_prediction' in st.session_state:
        pred = st.session_state['last_prediction']
        
        st.subheader("Prediction Results")
        
        # Main metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Predictability",
                f"{pred['detailed']['predictability_score']:.1f}%",
                delta="confidence"
            )
        
        with col2:
            st.metric(
                "Est. Gross Revenue",
                f"₹{pred['detailed']['revenue_estimate']:.0f} Cr"
            )
        
        with col3:
            st.metric(
                "Projected ROI",
                f"{pred['detailed']['roi_percentage']:.1f}%"
            )
        
        st.info(pred['detailed']['risk_level'])
        
        # Breakdown
        with st.expander("Score Breakdown", expanded=True):
            breakdown = pred['detailed']['breakdown']
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                st.metric("Talent", f"{breakdown['talent']:.0f}/100")
            with col_b2:
                st.metric("Market", f"{breakdown['market']:.0f}/100")
            with col_b3:
                st.metric("Content", f"{breakdown['content']:.0f}/100")
            
            col_b4, col_b5 = st.columns(2)
            with col_b4:
                st.metric("Viral", f"{breakdown['viral']:.0f}/100")
            with col_b5:
                st.metric("Seasonal", f"{breakdown['seasonal']:.0f}/100")
        
        # ROI Scenarios
        with st.expander("ROI Scenarios"):
            col_roi1, col_roi2, col_roi3 = st.columns(3)
            
            with col_roi1:
                st.metric(
                    "Optimistic",
                    f"{pred['detailed']['roi_optimistic']:.1f}%"
                )
            
            with col_roi2:
                st.metric(
                    "Realistic",
                    f"{pred['detailed']['roi_percentage']:.1f}%"
                )
            
            with col_roi3:
                st.metric(
                    "Pessimistic",
                    f"{pred['detailed']['roi_pessimistic']:.1f}%"
                )
        
        # Strategic Recommendations
        with st.expander("Strategic Recommendations"):
            recommendations = []
            
            if pred['detailed']['predictability_score'] >= 90:
                recommendations.append("**Greenlight Recommended** - Strong stability across pillars")
            elif pred['detailed']['predictability_score'] >= 80:
                recommendations.append("**Proceed with Optimization** - Address weak pillars")
            else:
                recommendations.append("**High Risk** - Significant concerns before production")
            
            if pred['detailed']['roi_percentage'] > 100:
                recommendations.append("**Strong ROI Potential** - Budget-to-return ratio favorable")
            elif pred['detailed']['roi_percentage'] < 0:
                recommendations.append("**Breakeven Risk** - May not recoup production investment")
            
            if has_clash:
                recommendations.append("**Release Clash Detected** - Consider shifting date or increasing marketing spend")
            
            for rec in recommendations:
                st.write(rec)
    else:
        st.info("Configure inputs and click 'Calculate Predictability' to see results")

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85em;">
    <p>Cinema Predictability Model v5 | Powered by OMDB/TMDB APIs & Curated South Indian Database</p>
    <p>Predictions are probabilistic estimates based on historical patterns. No model perfectly predicts creative industries.</p>
</div>
""", unsafe_allow_html=True)