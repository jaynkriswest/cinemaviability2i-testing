#Clde version updates with gemini + CGPT

# app.py - Corrected Version

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
from difflib import SequenceMatcher

# =====================================================
# IMPORT LOCAL MODULES
# =====================================================

from data import (
    GENRE_METRICS,
    SOUTH_INDIAN_ACTORS,
    DIRECTORS,
    SEASONAL_MULTIPLIERS,
)

from formula import (
    calculate_detailed_prediction,
)

# =====================================================
# SETUP
# =====================================================

load_dotenv()

st.set_page_config(
    page_title="v3i Cinema Predictor",
    layout="wide"
)

# =====================================================
# API KEY
# =====================================================

TMDB_API_KEY = (
    st.secrets.get("TMDB_API_KEY")
    or os.getenv("TMDB_API_KEY")
)

if not TMDB_API_KEY:
    st.error("Missing TMDB_API_KEY")
    st.stop()

# =====================================================
# DISPLAY HELPERS
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
# TMDB SEARCH
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

        response.raise_for_status()

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
                "Title": movie.get("title", "Unknown"),
                "Year": year,
                "tmdbID": movie.get("id")
            })

        return results

    except Exception as e:
        st.error(f"Search error: {e}")
        return []

# =====================================================
# FETCH DETAILS
# =====================================================

def fetch_detailed_data(tmdb_id):

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

        response.raise_for_status()

        tmdb = response.json()

        poster_path = tmdb.get("poster_path")

        poster_url = None

        if poster_path:
            poster_url = (
                f"https://image.tmdb.org/t/p/w500"
                f"{poster_path}"
            )

        genres = ", ".join(
            [
                genre["name"]
                for genre in tmdb.get("genres", [])
            ]
        )

        cast_names = ", ".join(
            [
                cast["name"]
                for cast in tmdb.get(
                    "credits",
                    {}
                ).get("cast", [])[:5]
            ]
        )

        movie_data = {
            "Title": tmdb.get("title", "Unknown"),
            "Year": tmdb.get(
                "release_date",
                ""
            )[:4],
            "Genre": genres,
            "Plot": tmdb.get(
                "overview",
                "No overview available."
            ),
            "Poster": poster_url,
            "Actors": cast_names,
        }

        return movie_data, tmdb

    except Exception as e:
        st.error(f"Movie detail error: {e}")
        return None, None

# =====================================================
# SIMILAR MOVIES
# =====================================================

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

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])[:10]

    except Exception as e:
        st.error(f"Similar movie error: {e}")
        return []

# =====================================================
# MOVIE DETAILS BY ID
# =====================================================

def get_movie_details_by_id(movie_id):

    try:

        url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}"
            f"?api_key={TMDB_API_KEY}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except:
        return {}

# =====================================================
# LIKENESS SCORE
# =====================================================

def calculate_likeness_score(
    movie_data,
    similar_movie
):

    score = 0

    current_genres = set(
        movie_data.get(
            "Genre",
            ""
        ).lower().split(",")
    )

    similar_genres = set(
        [
            genre["name"].lower()
            for genre in similar_movie.get(
                "genres",
                []
            )
        ]
    )

    genre_overlap = len(
        current_genres.intersection(
            similar_genres
        )
    )

    score += genre_overlap * 20

    title_similarity = SequenceMatcher(
        None,
        movie_data.get("Title", ""),
        similar_movie.get("title", "")
    ).ratio()

    score += title_similarity * 20

    popularity = similar_movie.get(
        "popularity",
        0
    )

    score += min(popularity / 5, 30)

    vote_average = similar_movie.get(
        "vote_average",
        0
    )

    score += vote_average * 3

    return round(min(score, 100), 1)

# =====================================================
# SUGGESTIONS ENGINE
# =====================================================

def generate_success_suggestions(
    report,
    release_date,
    budget,
    has_clash
):

    suggestions = []

    if has_clash:
        suggestions.append(
            "Avoid releasing during superstar clashes."
        )

    weak_months = [7, 8, 9]

    if release_date.month in weak_months:

        suggestions.append(
            "Shift release to January, April, October or December."
        )

    if budget > 250:

        suggestions.append(
            "Increase pan-India promotions and overseas distribution."
        )

    if report["predictability_score"] < 80:

        suggestions.append(
            "Increase trailer and teaser marketing."
        )

        suggestions.append(
            "Use influencer and social media campaigns."
        )

    if report["roi_percentage"] < 20:

        suggestions.append(
            "Reduce production cost or increase theatrical reach."
        )

    suggestions.append(
        "Target IMAX and premium multiplex screens."
    )

    suggestions.append(
        "Expand overseas distribution in USA, UAE and Australia."
    )

    return suggestions

# =====================================================
# TITLE
# =====================================================

st.title("v3i Cinema Predictability Dashboard")

st.markdown("---")

# =====================================================
# MAIN LAYOUT
# =====================================================

prediction_col, search_col = st.columns([1.1, 1])

# =====================================================
# LEFT SIDE - PREDICTION MONITOR
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
            85
            if market_multiplier > 1.0
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

    st.info(
        f"Risk Level: {report['risk_level']}"
    )

    st.subheader("Success Suggestions")

    suggestions = (
        generate_success_suggestions(
            report,
            release_date,
            budget,
            has_clash
        )
    )

    for suggestion in suggestions:
        st.write(f"• {suggestion}")

# =====================================================
# RIGHT SIDE - MOVIE SEARCH
# =====================================================

with search_col:

    st.header("Movie Search & Historical Similarities")

    search_query = st.text_input(
        "Search Movie",
        value="Apex"
    )

    movie_data = None
    tmdb_data = None

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

                movie_data, tmdb_data = (
                    fetch_detailed_data(
                        options[selected_label]
                    )
                )

    if movie_data:

        st.markdown("---")

        poster = movie_data.get("Poster")

        if poster:
            st.image(
                poster,
                use_container_width=True
            )

        st.subheader(
            f"{movie_data['Title']} "
            f"({movie_data['Year']})"
        )

        st.write(
            f"**Genre:** "
            f"{movie_data['Genre']}"
        )

        st.write(
            f"**Cast:** "
            f"{movie_data['Actors']}"
        )

        st.write(
            f"**Synopsis:** "
            f"{movie_data['Plot']}"
        )

        st.markdown("---")

        st.subheader(
            "Similar Historical Movies"
        )

        similar_movies = (
            get_similar_movies(
                options[selected_label]
            )
        )

        if similar_movies:

            for movie in similar_movies[:5]:

                detailed_movie = (
                    get_movie_details_by_id(
                        movie["id"]
                    )
                )

                likeness = (
                    calculate_likeness_score(
                        movie_data,
                        detailed_movie
                    )
                )

                title = detailed_movie.get(
                    "title",
                    "Unknown"
                )

                year = detailed_movie.get(
                    "release_date",
                    ""
                )[:4]

                rating = detailed_movie.get(
                    "vote_average",
                    "N/A"
                )

                popularity = detailed_movie.get(
                    "popularity",
                    0
                )

                revenue = detailed_movie.get(
                    "revenue",
                    0
                )

                budget_movie = detailed_movie.get(
                    "budget",
                    0
                )

                success_status = "Moderate"

                if revenue > budget_movie * 2:
                    success_status = "Blockbuster"

                elif revenue > budget_movie:
                    success_status = "Hit"

                elif revenue < budget_movie:
                    success_status = "Flop"

                st.markdown(
                    f"### {title} ({year})"
                )

                st.write(
                    f"Likeness Score: {likeness}%"
                )

                st.write(
                    f"TMDB Rating: {rating}"
                )

                st.write(
                    f"Popularity: "
                    f"{round(popularity, 1)}"
                )

                st.write(
                    f"Revenue: ${revenue:,}"
                )

                st.write(
                    f"Budget: ${budget_movie:,}"
                )

                st.write(
                    f"Performance: "
                    f"{success_status}"
                )

                st.markdown("---")