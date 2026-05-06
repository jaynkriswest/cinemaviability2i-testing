def calculate_v3i_logic(inputs):
    # 1. Core Pillar Calculation
    s_talent = inputs['talent_score']
    s_market = inputs['market_score']
    s_content = inputs['content_score']
    s_viral = inputs['viral_score']
    s_seasonal = inputs['seasonal_score']
    
    weighted_sum = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # 2. Global Multipliers
    final_prob = weighted_sum * inputs['m_cert'] * inputs['m_align']
    final_prob = min(final_prob, 99.0)

    # 3. Budget Efficiency Factor (NEW)
    # High budgets require High Talent Tiers to break even.
    efficiency = 1.0
    if inputs['budget'] > 150 and s_talent < 90:
        efficiency = 0.70  # 30% penalty for over-spending on low-tier talent
    elif inputs['budget'] > 250 and s_talent < 95:
        efficiency = 0.60  # Massive risk for mid-tier stars with mega-budgets[cite: 10]

    # 4. Realistic Revenue Calculation[cite: 5, 10]
    # Revenue is now scaled by predictability AND efficiency, not just budget.
    rev_multiplier = 1.4 if inputs['is_franchise'] else 1.0
    
    # Base market potential (Theatrical Cap)
    market_cap = 500  # Max potential for a massive hit in the current market[cite: 10]
    est_revenue = (final_prob / 100) * market_cap * efficiency * rev_multiplier
    
    # ROI Calculation
    roi_percent = ((est_revenue - inputs['budget']) / inputs['budget']) * 100

    return final_prob, est_revenue, roi_percent