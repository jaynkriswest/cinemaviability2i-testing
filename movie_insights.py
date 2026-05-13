from difflib import SequenceMatcher

# =====================================================
# LIKENESS SCORE: CGPT version
# =====================================================

def calculate_likeness_score(
    current_movie,
    comparison_movie
):

    score = 0

    current_genres = set(
        current_movie.get(
            "Genre",
            ""
        ).lower().split(",")
    )

    comparison_genres = set(
        [
            genre["name"].lower()
            for genre in comparison_movie.get(
                "genres",
                []
            )
        ]
    )

    genre_overlap = len(
        current_genres.intersection(
            comparison_genres
        )
    )

    score += genre_overlap * 20

    title_similarity = SequenceMatcher(
        None,
        current_movie.get("Title", ""),
        comparison_movie.get("title", "")
    ).ratio()

    score += title_similarity * 15

    popularity = comparison_movie.get(
        "popularity",
        0
    )

    score += min(popularity / 4, 25)

    vote_average = comparison_movie.get(
        "vote_average",
        0
    )

    score += vote_average * 3

    return round(min(score, 100), 1)

# =====================================================
# SUCCESS CLASSIFICATION
# =====================================================

def classify_movie_success(movie):

    revenue = movie.get("revenue", 0)
    budget = movie.get("budget", 1)

    if budget <= 0:
        budget = 1

    roi = revenue / budget

    if roi >= 3:
        return "Blockbuster"

    elif roi >= 1.5:
        return "Hit"

    elif roi >= 1:
        return "Average"

    return "Flop"

# =====================================================
# SUCCESS REASONS
# =====================================================

def analyze_success_reasons(movie):

    reasons = []

    popularity = movie.get("popularity", 0)
    revenue = movie.get("revenue", 0)
    budget = movie.get("budget", 1)
    runtime = movie.get("runtime", 0)

    roi = revenue / max(budget, 1)

    if popularity > 80:

        reasons.append(
            "Strong audience engagement and awareness."
        )

    if roi > 2:

        reasons.append(
            "Excellent commercial ROI efficiency."
        )

    if runtime < 170:

        reasons.append(
            "Audience-friendly runtime helped theatrical pull."
        )

    genres = [
        genre["name"]
        for genre in movie.get(
            "genres",
            []
        )
    ]

    if "Action" in genres:

        reasons.append(
            "Mass-market action appeal improved collections."
        )

    return reasons

# =====================================================
# FAILURE REASONS
# =====================================================

def analyze_failure_reasons(movie):

    reasons = []

    revenue = movie.get("revenue", 0)
    budget = movie.get("budget", 1)
    popularity = movie.get("popularity", 0)
    runtime = movie.get("runtime", 0)

    roi = revenue / max(budget, 1)

    if roi < 1:

        reasons.append(
            "Weak commercial ROI performance."
        )

    if budget > 250000000:

        reasons.append(
            "Oversized production budget increased risk."
        )

    if popularity < 40:

        reasons.append(
            "Low audience engagement and buzz."
        )

    if runtime > 180:

        reasons.append(
            "Excessive runtime likely reduced repeat audiences."
        )

    return reasons