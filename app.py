#Updated from Main folder updated from testing (Cldegem1i)

# app.py - updated version

import streamlit as st
import requests
import os

from dotenv import load_dotenv
from datetime import date

from data import (
    GENRE_METRICS,
    SOUTH_INDIAN_ACTORS,
    DIRECTORS,
    SEASONAL_MULTIPLIERS,
)

from formula import (
    calculate_detailed_prediction,
)

from movie_insights import (
    search_movies_by_synopsis,
    fetch_full_movie_details,
    calculate_future_likeness,
    classify_movie_success,
    analyze_success_reasons,
    analyze_failure_reasons,
)

# =====================================================
# SETUP
# =====================================================

load_dotenv()

st.set_page_config(
    page_title="Cinema Intelligence Platform",
    layout="wide"
)

TMDB_API_KEY = (
    st.secrets.get("TMDB_API_KEY")
    or os.getenv("TMDB_API_KEY")
)

if not TMDB_API_KEY:
    st.error("Missing TMDB_API_KEY")
    st.stop()

# =====================================================
# DISPLAY MAPS
# =====================================================

ACTOR_DISPLAY_MAP = {
    key: key.replace("_", " ").title()
    for key in SOUTH_INDIAN_ACTORS.keys()
}

DIRECTOR_DISPLAY_MAP = {
    key: key.replace("_", " ").title()
    for key in DIRECTORS.keys()
}

# =====================================================
# SEARCH FUNCTIONS
# =====================================================

def search_movies_list(query):

    try:

        url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_API_KEY}"
            f"&query={query}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        results = []

        for movie in data.get("results", []):

            release_date = movie.get(
                "release_date",
                ""
            )

            year = (
                release_date[:4]
                if release_date
                else "Unknown"
            )

            results.append({
                "Title": movie.get("title"),
                "Year": year,
                "tmdbID": movie.get("id")
            })

        return results

    except:
        return []

def fetch_movie(tmdb_id):

    try:

        url = (
            f"https://api.themoviedb.org/3/movie/{tmdb_id}"
            f"?api_key={TMDB_API_KEY}"
            f"&append_to_response=credits"
        )

        response = requests.get(
            url,
            timeout=15
        )

        movie = response.json()

        poster_path = movie.get(
            "poster_path"
        )

        poster = None

        if poster_path:

            poster = (
                "https://image.tmdb.org/t/p/w500"
                f"{poster_path}"
            )

        movie_data = {
            "Title": movie.get("title"),
            "Year": movie.get(
                "release_date",
                ""
            )[:4],
            "Genre": ", ".join(
                [
                    genre["name"]
                    for genre in movie.get(
                        "genres",
                        []
                    )
                ]
            ),
            "Plot": movie.get("overview"),
            "Poster": poster,
            "Actors": ", ".join(
                [
                    cast["name"]
                    for cast in movie.get(
                        "credits",
                        {}
                    ).get("cast", [])[:5]
                ]
            )
        }

        return movie_data, movie

    except:
        return None, None

def get_similar_movies(tmdb_id):

    try:

        url = (
            f"https://api.themoviedb.org/3/movie/{tmdb_id}/similar"
            f"?api_key={TMDB_API_KEY}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        return data.get("results", [])[:5]

    except:
        return []

# =====================================================
# TITLE
# =====================================================

st.title("Cinema Intelligence Platform")

# =====================================================
# LAYOUT
# =====================================================

prediction_col, search_col = st.columns([1.2, 1])

# =====================================================
# LEFT SIDE — FUTURE FILM PREDICTION
# =====================================================

with prediction_col:

    st.header("Prediction Monitor")

    movie_synopsis = st.text_area(
        "Future Movie Synopsis",
        placeholder=(
            "Describe the future movie concept..."
        )
    )

    genre = st.selectbox(
        "Genre",
        list(GENRE_METRICS.keys())
    )

    actor_key = st.selectbox(
        "Lead Actor",
        list(SOUTH_INDIAN_ACTORS.keys()),
        format_func=lambda x:
        ACTOR_DISPLAY_MAP[x]
    )

    director_key = st.selectbox(
        "Director",
        list(DIRECTORS.keys()),
        format_func=lambda x:
        DIRECTOR_DISPLAY_MAP[x]
    )

    release_date = st.date_input(
        "Release Date",
        value=date(2026, 1, 12)
    )

    has_clash = st.checkbox(
        "Superstar Clash?"
    )

    budget = st.number_input(
        "Budget (Crores)",
        min_value=1.0,
        value=100.0
    )

    # =====================================================
    # BUTTONS
    # =====================================================

    run_prediction = st.button(
        "Run Prediction",
        use_container_width=True
    )

    reset_prediction = st.button(
        "Reset",
        use_container_width=True
    )

    if reset_prediction:

        st.session_state.clear()

        st.rerun()

    # =====================================================
    # PREDICTION ENGINE
    # =====================================================

    if run_prediction:

        market_multiplier = (
            SEASONAL_MULTIPLIERS.get(
                release_date.month,
                1.0
            )
        )

        calc_inputs = {

            "talent_score": (
                SOUTH_INDIAN_ACTORS[actor_key]["score"]
                + DIRECTORS[director_key]["score"]
            ) / 2,

            "market_base": 85,

            "market_multiplier": market_multiplier,

            "has_clash": has_clash,

            "content_score": (
                GENRE_METRICS[genre]["base_score"]
            ),

            "viral_score": 75,

            "seasonal_score": (
                85 if market_multiplier > 1.0
                else 70
            ),

            "m_cert": 1.0,

            "budget": budget,
        }

        report = calculate_detailed_prediction(
            calc_inputs
        )

        # =====================================================
        # PREDICTION RESULTS
        # =====================================================

        st.subheader("Prediction Results")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Predictability",
            f"{report['predictability_score']}%"
        )

        c2.metric(
            "Revenue",
            f"₹{report['revenue_estimate']} Cr"
        )

        c3.metric(
            "ROI",
            f"{report['roi_percentage']}%"
        )

        # =====================================================
        # FUTURE FILM MATCHING
        # =====================================================

        if movie_synopsis:

            st.markdown("---")

            st.subheader(
                "Closest Historical Matches"
            )

            historical_matches = (
                search_movies_by_synopsis(
                    movie_synopsis,
                    TMDB_API_KEY
                )
            )

            if not historical_matches:

                st.warning(
                    "No historical matches found."
                )

            for movie in historical_matches:

                likeness = (
                    calculate_future_likeness(
                        movie_synopsis,
                        genre,
                        movie
                    )
                )

                detailed_movie = (
                    fetch_full_movie_details(
                        movie["id"],
                        TMDB_API_KEY
                    )
                )

                performance = (
                    classify_movie_success(
                        detailed_movie
                    )
                )

                st.markdown(
                    f"### {movie['title']}"
                )

                st.write(
                    f"Likeness Score: "
                    f"{likeness}%"
                )

                st.write(
                    f"Performance: "
                    f"{performance}"
                )

                # =====================================================
                # SUCCESS ANALYSIS
                # =====================================================

                success_reasons = (
                    analyze_success_reasons(
                        detailed_movie
                    )
                )

                if success_reasons:

                    st.success(
                        "Why It Worked"
                    )

                    for reason in success_reasons:

                        st.write(
                            f"• {reason}"
                        )

                # =====================================================
                # FAILURE ANALYSIS
                # =====================================================

                failure_reasons = (
                    analyze_failure_reasons(
                        detailed_movie
                    )
                )

                if failure_reasons:

                    st.error(
                        "Why It Failed"
                    )

                    for reason in failure_reasons:

                        st.write(
                            f"• {reason}"
                        )

                st.markdown("---")

# =====================================================
# RIGHT SIDE — MOVIE SEARCH
# =====================================================

with search_col:

    st.header("Movie Search")

    search_query = st.text_input(
        "Search Movie",
        value="Apex"
    )

    movie_data = None
    tmdb_movie = None

    if search_query:

        search_results = search_movies_list(
            search_query
        )

        if search_results:

            options = {

                f"{movie['Title']} "
                f"({movie['Year']})":

                movie["tmdbID"]

                for movie in search_results
            }

            selected_label = st.selectbox(
                "Select Movie",
                list(options.keys())
            )

            if selected_label:

                movie_data, tmdb_movie = (
                    fetch_movie(
                        options[selected_label]
                    )
                )

    if movie_data:

        if movie_data["Poster"]:

            st.image(
                movie_data["Poster"],
                use_container_width=True
            )

        st.subheader(
            f"{movie_data['Title']} "
            f"({movie_data['Year']})"
        )

        st.write(
            f"Genre: "
            f"{movie_data['Genre']}"
        )

        st.write(
            f"Cast: "
            f"{movie_data['Actors']}"
        )

        st.write(
            movie_data["Plot"]
        )

        st.markdown("---")

        st.subheader(
            "Similar Historical Films"
        )

        similar_movies = get_similar_movies(
            options[selected_label]
        )

        for movie in similar_movies:

            st.markdown(
                f"• {movie.get('title')}"
            )

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