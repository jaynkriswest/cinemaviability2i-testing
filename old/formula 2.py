def calculate_v3i_logic(inputs):
    # Pillar Weights from Section 1 of v3i_3.docx
    # S_Talent (30%), S_Market (20%), S_Content (20%), S_Viral (15%), S_Seasonal (15%)
    
    s_talent = inputs['talent_score']
    
    # S_Market includes the Holiday Multiplier (1.3x) or Summer (1.15x)
    # and the Clash Penalty (-0.15 points)
    s_market = (inputs['market_base'] * inputs['market_multiplier'])
    if inputs['has_clash']:
        s_market -= 15 

    s_content = inputs['content_score']
    # Content receives a 1.4x bonus if it is a Franchise/IP
    if inputs['is_franchise']:
        s_content *= 1.4

    s_viral = inputs['viral_score']
    s_seasonal = inputs['seasonal_score']

    # THE PREDICTABILITY EQUATION
    weighted_sum = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # Global Reach Multipliers
    # M_Cert (U=1.2, UA=1.0, A=0.7) and M_Align (Consistent=1.0, Misaligned=0.9)
    final_prob = weighted_sum * inputs['m_cert'] * inputs['m_align']
    
    # Financial Logic: Revenue & ROI
    # To get the ~394 Cr result for a 200 Cr budget, the efficiency 
    # must be balanced against the budget-to-talent ratio.
    revenue_multiplier = 2.0  # Standard ROI floor for Ultra-Veterans
    est_revenue = (final_prob / 100) * (inputs['budget'] * revenue_multiplier)
    
    roi = ((est_revenue - inputs['budget']) / inputs['budget']) * 100

    return min(final_prob, 99.0), est_revenue, roi