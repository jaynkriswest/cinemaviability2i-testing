def calculate_v3i_logic(inputs):
    # Standard weighted pillars from your document
    s_talent = inputs['talent_score']
    s_market = inputs['market_multiplier'] * 85
    s_content = inputs['content_score']
    s_viral = inputs['viral_score']
    s_seasonal = inputs['seasonal_score']
    
    # 1. The Predictability Equation
    base_sum = (
        (s_talent * 0.30) + (s_market * 0.20) + (s_content * 0.20) + 
        (s_viral * 0.15) + (s_seasonal * 0.15)
    )
    final_prob = base_sum * inputs['m_cert'] * inputs['m_align']
    
    # 2. INTRODUCE MARKET CEILING (Section 6: Technical Constraints)
    # For a regional hit, the cap is around 400Cr unless Viral is 'High'
    theatrical_cap = 380 
    if s_viral >= 90: theatrical_cap = 650 # Only 'High' Viral hits the mega-numbers
    
    # 3. Calculate Revenue based on Probability of hitting that Cap
    est_revenue = (final_prob / 100) * theatrical_cap
    
    # 4. ROI Calculation
    roi = ((est_revenue - inputs['budget']) / inputs['budget']) * 100

    return min(final_prob, 99.0), est_revenue, roi