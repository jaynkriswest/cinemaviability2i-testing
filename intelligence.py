# =====================================================
# COMMERCIAL VIABILITY
# =====================================================

def calculate_commercial_viability(
    report,
    budget,
    genre,
    has_clash,
    release_date
):

    viability = 100

    if budget > 250:
        viability -= 15

    if has_clash:
        viability -= 10

    if release_date.month in [7, 8, 9]:
        viability -= 8

    if genre == "Romance":
        viability -= 5

    viability += min(
        report["roi_percentage"] / 10,
        12
    )

    viability = max(0, min(100, viability))

    if viability >= 85:
        label = "Strong Greenlight"

    elif viability >= 70:
        label = "Commercially Viable"

    elif viability >= 55:
        label = "High Risk"

    else:
        label = "Not Commercially Safe"

    return {
        "score": round(viability, 1),
        "label": label
    }

# =====================================================
# STRATEGIC ACTIONS
# =====================================================

def generate_producer_actions(
    report,
    budget,
    genre,
    has_clash,
    release_date
):

    actions = []

    if release_date.month in [7, 8, 9]:

        actions.append(
            "Shift release to October or January."
        )

    if has_clash:

        actions.append(
            "Avoid releasing near superstar films."
        )

    if budget > 250:

        actions.append(
            "Reduce production cost or improve overseas expansion."
        )

    if genre == "Action":

        actions.append(
            "Focus marketing on action-heavy teaser cuts."
        )

    if report["predictability_score"] < 80:

        actions.append(
            "Increase teaser and social media marketing."
        )

    actions.append(
        "Prioritize IMAX and premium multiplex screens."
    )

    actions.append(
        "Increase Telugu + Hindi promotions."
    )

    return actions

# =====================================================
# DON’TS ENGINE
# =====================================================

def generate_producer_warnings(
    budget,
    genre,
    has_clash,
    release_date
):

    warnings = []

    if budget > 300:

        warnings.append(
            "Do NOT inflate VFX budgets unnecessarily."
        )

    if has_clash:

        warnings.append(
            "Do NOT release near tier-1 superstar movies."
        )

    if release_date.month in [7, 8, 9]:

        warnings.append(
            "Do NOT release during weak monsoon windows."
        )

    if genre == "Romance":

        warnings.append(
            "Do NOT overspend theatrically for romance films."
        )

    warnings.append(
        "Do NOT overexpose songs before release."
    )

    warnings.append(
        "Do NOT exceed excessive runtime."
    )

    return warnings

# =====================================================
# THEATER STRATEGY
# =====================================================

def calculate_theater_strategy(
    predictability,
    budget,
    genre
):

    india_screens = 1500
    overseas_screens = 250

    if predictability >= 90:

        india_screens = 3200
        overseas_screens = 700

    elif predictability >= 80:

        india_screens = 2400
        overseas_screens = 500

    elif predictability >= 70:

        india_screens = 1800
        overseas_screens = 350

    if genre == "Action":
        india_screens += 300

    if budget > 250:
        overseas_screens += 100

    return {
        "india_screens": india_screens,
        "overseas_screens": overseas_screens,
        "multiplex_share": 60,
        "single_screen_share": 40
    }