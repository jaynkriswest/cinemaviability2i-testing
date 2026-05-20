# movie_insights.py - Completed Production Synchronization Version

import requests
from difflib import SequenceMatcher

# =====================================================
# SEARCH MOVIES USING FUTURE SYNOPSIS
# =====================================================

def search_movies_by_synopsis(synopsis, api_key):
    """
    Finds historical archetype films from TMDB based on matching text criteria.
    Calculates a dynamic thematic likeness metric via comparison matrices.
    """
    try:
        if not synopsis:
            return []
            
        synopsis_lower = synopsis.lower()
        
        # Pull popular Indian movies to cross-reference text structures
        url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": api_key,
            "region": "IN",
            "sort_by": "popularity.desc",
            "page": 1
        }
        
        res = requests.get(url, params=params, timeout=5)
        results = res.json().get("results", [])
        
        compiled_comps = []
        for movie in results:
            overview = movie.get("overview", "")
            if not overview:
                continue
                
            # Calculate thematic matching ratio
            ratio = SequenceMatcher(None, synopsis_lower, overview.lower()).ratio()
            
            # Calibrate similarity scoring to a distribution between 30% and 98%
            likeness_score = min(round((ratio * 100) * 4 + 30, 1), 98.5)
            
            compiled_comps.append({
                "title": movie.get("title", "Unknown Archetype"),
                "release_year": movie.get("release_date", "####")[:4],
                "historical_overview": overview,
                "overview": overview,  # Maintained for backward compatibility in tab layouts
                "likeness_score": likeness_score
            })
            
        # Return top 3 strongest narrative archetypes
        return sorted(compiled_comps, key=lambda x: x["likeness_score"], reverse=True)[:3]
        
    except Exception as e:
        return []

# =====================================================
# FETCH DETAILED DATA METRICS
# =====================================================

def fetch_full_movie_details(movie_id, api_key):
    """
    Retrieves deep production metrics from TMDB for financial analysis grids.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": api_key}
    try:
        res = requests.get(url, params=params, timeout=5)
        return res.json()
    except Exception:
        return {}

# =====================================================
# ANALYTICS MULTIPLIERS & STRATEGIC LOGIC
# =====================================================

def calculate_future_likeness(synopsis, historical_overview):
    """
    Calculates inline similarity variations when comparing two static abstracts.
    """
    if not synopsis or not historical_overview:
        return 50.0
    ratio = SequenceMatcher(None, synopsis.lower(), historical_overview.lower()).ratio()
    return min(round(ratio * 100 * 2 + 20, 1), 100.0)

def classify_movie_success(revenue, budget):
    """
    Categorizes traditional commercial performance tier models.
    """
    if not budget or budget <= 0:
        return "Unknown Status"
    roi = revenue / budget
    if roi >= 2.5:
        return "Blockbuster Verdict"
    elif roi >= 1.5:
        return "Commercially Profitable"
    elif roi >= 1.0:
        return "Recovered Costs (Breakeven)"
    else:
        return "Financial Deficit"

def analyze_success_reasons(inputs):
    """
    Generates strategic diagnostic checklists highlighting high-yield multipliers.
    """
    reasons = []
    if inputs.get("talent_score", 0) >= 85:
        reasons.append("High-tier talent composition anchoring theater footfalls.")
    if inputs.get("viral_score", 0) >= 80:
        reasons.append("Strong organic promotional hype acceleration track.")
    if inputs.get("is_franchise"):
        reasons.append("Built-in box office floor supported by active intellectual property sequel value.")
    if inputs.get("m_align", 0.0) >= 0.95:
        reasons.append("Marketing messaging framework perfectly matches audience expectations.")
    return reasons

def analyze_failure_reasons(inputs):
    """
    Generates critical risk logs flagging structural commercial constraints.
    """
    reasons = []
    if inputs.get("budget", 0) > 200:
        reasons.append("High budget exposure capital requirements significantly elevate ROI risk thresholds.")
    if inputs.get("has_clash"):
        reasons.append("Holiday release clash fragments initial market box office distribution potential.")
    if inputs.get("m_cert", 1.0) < 1.0:
        reasons.append("Adult ('A') classification constraints structurally limit theater seating distribution ceilings.")
    if inputs.get("seasonal_score", 100) < 80:
        reasons.append("Target launch window sits outside optimal holiday consumption cycles.")
    return reasons