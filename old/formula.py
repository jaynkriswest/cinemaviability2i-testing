def calculate_cinema_logic(talent_score, genre_weight, season_multiplier, budget, target_market):
    """
    Advanced Interaction Logic for Cinema Predictability.
    """
    # 1. Base Score calculation
    base_score = (talent_score * 0.4) + (genre_weight * 0.3) + (target_market * 0.3)

    # 2. Interaction Multiplier Block: Synergy between Veteran Talent and Festivals
    # Veterans + Festive releases (like Sankranthi) often over-perform
    synergy_bonus = 1.0
    if talent_score > 90 and season_multiplier > 1.1:
        synergy_bonus = 1.15  # 15% boost for "Mega" synergy

    # 3. Budget-Risk Penalty
    # High budgets without Pan-India appeal are mathematically riskier
    risk_penalty = 1.0
    if budget > 100 and target_market < 80:
        risk_penalty = 0.85  # 15% penalty for budget-market mismatch

    final_probability = base_score * season_multiplier * synergy_bonus * risk_penalty
    
    # Cap the probability at 99% for logical realism
    return min(final_probability, 99.0)