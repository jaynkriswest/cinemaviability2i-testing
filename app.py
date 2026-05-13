#Clde version updates with gemini + CGPT

# app.py - Corrected Version

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

from intelligence import (
    calculate_commercial_viability,
    generate_producer_actions,
    generate_producer_warnings,
    calculate_theater_strategy,
)

from movie_insights import (
    calculate_likeness_score,
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

        response = requests.get(url)

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

        response = requests.get(url)

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

        response = requests.get(url)

        data = response.json()

        return data.get("results", [])[:5]

    except:
        return []

# =====================================================
# TITLE
# =====================================================

st.title("Cinema Intelligence & Greenlight Platform")

# =====================================================
# LAYOUT
# =====================================================

prediction_col, search_col = st.columns([1.2, 1])

# =====================================================
# LEFT SIDE
# =====================================================

with prediction_col:

    st.header("Prediction Monitor")

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
    # COMMERCIAL VIABILITY
    # =====================================================

    viability = calculate_commercial_viability(
        report,
        budget,
        genre,
        has_clash,
        release_date
    )

    st.subheader("Commercial Viability")

    st.metric(
        "Viability Score",
        f"{viability['score']}%"
    )

    st.success(
        viability["label"]
    )

    # =====================================================
    # PRODUCER ACTIONS
    # =====================================================

    st.subheader(
        "Strategic Producer Actions"
    )

    producer_actions = (
        generate_producer_actions(
            report,
            budget,
            genre,
            has_clash,
            release_date
        )
    )

    for action in producer_actions:
        st.write(f"• {action}")

    # =====================================================
    # DON’TS
    # =====================================================

    st.subheader("Critical DON’Ts")

    warnings = (
        generate_producer_warnings(
            budget,
            genre,
            has_clash,
            release_date
        )
    )

    for warning in warnings:
        st.error(warning)

    # =====================================================
    # THEATER STRATEGY
    # =====================================================

    theater_strategy = (
        calculate_theater_strategy(
            report["predictability_score"],
            budget,
            genre
        )
    )

    st.subheader("Theater Strategy")

    st.write(
        f"India Screens: "
        f"{theater_strategy['india_screens']}"
    )

    st.write(
        f"Overseas Screens: "
        f"{theater_strategy['overseas_screens']}"
    )

    st.write(
        f"Multiplex Share: "
        f"{theater_strategy['multiplex_share']}%"
    )

    st.write(
        f"Single Screen Share: "
        f"{theater_strategy['single_screen_share']}%"
    )

# =====================================================
# RIGHT SIDE
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

            detailed_movie, raw_movie = (
                fetch_movie(movie["id"])
            )

            likeness = (
                calculate_likeness_score(
                    movie_data,
                    raw_movie
                )
            )

            success = (
                classify_movie_success(
                    raw_movie
                )
            )

            st.markdown(
                f"### {raw_movie.get('title')} "
                f"({raw_movie.get('release_date', '')[:4]})"
            )

            st.write(
                f"Likeness Score: {likeness}%"
            )

            st.write(
                f"Performance: {success}"
            )

            # =====================================================
            # SUCCESS ANALYSIS
            # =====================================================

            if success in [
                "Blockbuster",
                "Hit"
            ]:

                reasons = (
                    analyze_success_reasons(
                        raw_movie
                    )
                )

                st.success(
                    "Why It Worked"
                )

                for reason in reasons:
                    st.write(f"• {reason}")

            else:

                reasons = (
                    analyze_failure_reasons(
                        raw_movie
                    )
                )

                st.error(
                    "Why It Failed"
                )

                for reason in reasons:
                    st.write(f"• {reason}")

            st.markdown("---")