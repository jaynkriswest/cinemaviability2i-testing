# formula.py

def calculate_v3i_logic(inputs):
    """
    Implements Predictability (%) = [Weighted Pillars] x M_Cert x M_Align
    """
    # 1. Extract Pillar Scores
    s_talent = inputs['talent_score']
    s_market = inputs['market_score']
    s_content = inputs['content_score']
    s_viral = inputs['viral_score']
    s_seasonal = inputs['seasonal_score']
    
    # 2. Weighted Sum (The Core Probability)
    core_sum = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # 3. Apply Global Reach Multipliers
    # M_Cert: U (1.2), UA (1.0), A (0.7)
    # M_Align: Consistent (1.0), Misaligned (0.9)
    final_predictability = core_sum * inputs['m_cert'] * inputs['m_align']
    
    # 4. ROI Prediction
    # ROI = ((Revenue - Budget) / Budget) * 100
    # Revenue is scaled by the predictability score and franchise bonuses
    revenue_multiplier = 1.4 if inputs['is_franchise'] else 1.0
    est_revenue = (final_predictability / 100) * (inputs['budget'] * 2.5) * revenue_multiplier
    roi = ((est_revenue - inputs['budget']) / inputs['budget']) * 100

    return min(final_predictability, 99.0), roi