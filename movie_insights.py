import requests
from difflib import SequenceMatcher

# =====================================================
# SEARCH MOVIES USING FUTURE SYNOPSIS
# =====================================================

def search_movies_by_synopsis(
    synopsis,
    api_key
):

    try:

        synopsis_lower = synopsis.lower()

        # =================================================
        # SMART KEYWORD DETECTION
        # =================================================

        keywords = []

        keyword_map = {

            "superhero": [
                "superhero",
                "powers",
                "villain",
                "hero"
            ],

            "action": [
                "fight",
                "violence",
                "gang",
                "revenge",
                "mass",
                "criminal",
                "corruption"
            ],

            "horror": [
                "ghost",
                "haunted",
                "spirit",
                "supernatural"
            ],

            "sports": [
                "athlete",
                "sports",
                "cricket",
                "football",
                "boxing"
            ],

            "sci-fi": [
                "robot",
                "technology",
                "future",
                "space",
                "alien"
            ],

            "fantasy": [
                "kingdom",
                "magic",
                "warrior",
                "ancient"
            ]
        }

        # =================================================
        # DETECT KEYWORDS FROM SYNOPSIS
        # =================================================

        for category, words in keyword_map.items():

            for word in words:

                if word in synopsis_lower:

                    keywords.append(word)

        # =================================================
        # FALLBACK KEYWORDS
        # =================================================

        if not keywords:

            keywords = [
                word for word in synopsis.split()
                if len(word) > 5
            ][:5]

        # =================================================
        # FINAL QUERY
        # =================================================

        query = " ".join(keywords)

        # Safety fallback
        if not query:
            query = synopsis[:40]

        # Debugging
        print("TMDB QUERY:", query)

        # =================================================
        # TMDB SEARCH
        # =================================================

        url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={api_key}"
            f"&query={query}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])[:5]

    except Exception as e:

        print("TMDB SEARCH ERROR:", e)

        return []

# =====================================================
# FETCH FULL MOVIE DETAILS
# =====================================================

def fetch_full_movie_details(
    movie_id,
    api_key
):

    try:

        url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}"
            f"?api_key={api_key}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print("DETAIL FETCH ERROR:", e)

        return {}

# =====================================================
# FUTURE FILM LIKENESS SCORE
# =====================================================

def calculate_future_likeness(
    future_synopsis,
    future_genre,
    historical_movie
):

    score = 0

    # =====================================================
    # SYNOPSIS SIMILARITY
    # =====================================================

    overview = historical_movie.get(
        "overview",
        ""
    )

    synopsis_similarity = (
        SequenceMatcher(
            None,
            future_synopsis.lower(),
            overview.lower()
        ).ratio()
    )

    score += synopsis_similarity * 70

    # =====================================================
    # POPULARITY WEIGHTING
    # =====================================================

    popularity = historical_movie.get(
        "popularity",
        0
    )

    score += min(popularity / 10, 15)

    # =====================================================
    # VOTE AVERAGE
    # =====================================================

    vote_average = historical_movie.get(
        "vote_average",
        0
    )

    score += vote_average

    # =====================================================
    # FINAL SCORE
    # =====================================================

    final_score = round(
        min(score, 100),
        1
    )

    return final_score

# =====================================================
# PERFORMANCE CLASSIFICATION
# =====================================================

def classify_movie_success(movie):

    revenue = movie.get(
        "revenue",
        0
    )

    budget = movie.get(
        "budget",
        1
    )

    if budget <= 0:
        return "Unknown"

    roi = revenue / budget

    if roi >= 3:
        return "Blockbuster"

    elif roi >= 1.5:
        return "Hit"

    elif roi >= 1:
        return "Average"

    return "Flop"

# =====================================================
# SUCCESS ANALYSIS
# =====================================================

def analyze_success_reasons(movie):

    reasons = []

    popularity = movie.get(
        "popularity",
        0
    )

    vote_average = movie.get(
        "vote_average",
        0
    )

    runtime = movie.get(
        "runtime",
        0
    )

    revenue = movie.get(
        "revenue",
        0
    )

    budget = movie.get(
        "budget",
        1
    )

    roi = revenue / max(budget, 1)

    # =====================================================
    # POPULARITY
    # =====================================================

    if popularity > 80:

        reasons.append(
            "Strong audience engagement and awareness."
        )

    # =====================================================
    # ROI
    # =====================================================

    if roi > 2:

        reasons.append(
            "Excellent commercial ROI efficiency."
        )

    # =====================================================
    # RATINGS
    # =====================================================

    if vote_average > 7:

        reasons.append(
            "Positive audience reception and ratings."
        )

    # =====================================================
    # RUNTIME
    # =====================================================

    if runtime < 170 and runtime > 0:

        reasons.append(
            "Audience-friendly runtime supported theatrical performance."
        )

    # =====================================================
    # GENRE ANALYSIS
    # =====================================================

    genres = [
        genre["name"]
        for genre in movie.get(
            "genres",
            []
        )
    ]

    if "Action" in genres:

        reasons.append(
            "Strong mass-market action appeal."
        )

    if "Family" in genres:

        reasons.append(
            "Broad family audience accessibility."
        )

    if "Adventure" in genres:

        reasons.append(
            "Large-scale adventure appeal increased audience reach."
        )

    if "Science Fiction" in genres:

        reasons.append(
            "High-concept sci-fi appeal attracted curiosity."
        )

    return reasons

# =====================================================
# FAILURE ANALYSIS
# =====================================================

def analyze_failure_reasons(movie):

    reasons = []

    popularity = movie.get(
        "popularity",
        0
    )

    runtime = movie.get(
        "runtime",
        0
    )

    revenue = movie.get(
        "revenue",
        0
    )

    budget = movie.get(
        "budget",
        1
    )

    roi = revenue / max(budget, 1)

    # =====================================================
    # WEAK ROI
    # =====================================================

    if roi < 1:

        reasons.append(
            "Weak commercial ROI performance."
        )

    # =====================================================
    # LOW POPULARITY
    # =====================================================

    if popularity < 40:

        reasons.append(
            "Low audience engagement and buzz."
        )

    # =====================================================
    # LONG RUNTIME
    # =====================================================

    if runtime > 180:

        reasons.append(
            "Excessive runtime may reduce repeat viewership."
        )

    # =====================================================
    # HIGH BUDGET RISK
    # =====================================================

    if budget > 250000000:

        reasons.append(
            "High production budget increased financial risk."
        )

    # =====================================================
    # LOW RATINGS
    # =====================================================

    vote_average = movie.get(
        "vote_average",
        0
    )

    if vote_average < 5:

        reasons.append(
            "Weak audience reception and ratings."
        )

    return reasons