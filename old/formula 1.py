# formula.py

def calculate_v3i_logic(inputs):
    # Pillar Scores
    s_talent = inputs['talent_score']
    s_market = inputs['market_score']
    s_content = inputs['content_score']
    s_viral = inputs['viral_score']
    s_seasonal = inputs['seasonal_score']
    
    # 1. The Predictability Equation: Weighted Sum
    weighted_sum = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # 2. Global Reach Multipliers
    # M_Cert (U: 1.2, UA: 1.0, A: 0.7)
    # M_Align (Consistent: 1.0, Misaligned: 0.9)
    final_predictability = weighted_sum * inputs['m_cert'] * inputs['m_align']
    
    # 3. Financial Projection (ROI)
    # Incorporating the 'ROI Stability Floor' for Ultra-Veterans
    stability_bonus = 1.2 if s_talent >= 95 else 1.0
    est_revenue = (final_predictability / 100) * (inputs['budget'] * 2.6) * stability_bonus
    roi = ((est_revenue - inputs['budget']) / inputs['budget']) * 100

    return min(final_predictability, 99.0), est_revenue, roi