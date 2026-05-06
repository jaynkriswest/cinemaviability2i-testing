from datetime import date

def calculate_v3i_logic(inputs):
    s_talent = inputs['talent_score']
    s_content = inputs['content_score']
    s_viral = inputs['viral_score']
    rel_date = inputs['release_date']
    
    # 1. UNIVERSAL DATE LOGIC (Pillar 2 & 3)
    s_market = 70  # Baseline
    s_seasonal = 70 # Baseline
    
    # Sankranti / Pongal Window (Always Jan 13-17)
    if rel_date.month == 1 and 13 <= rel_date.day <= 17:
        s_market, s_seasonal = 100, 95
    
    # Summer Vacation (Always late April to early June)
    elif (rel_date.month == 4 and rel_date.day >= 20) or rel_date.month == 5 or (rel_date.month == 6 and rel_date.day <= 10):
        s_market, s_seasonal = 90, 90
    
    # Independence Day (Always mid-August)
    elif rel_date.month == 8 and 12 <= rel_date.day <= 16:
        s_market, s_seasonal = 95, 85

    # Dussehra / Diwali Window (Varies, but usually Oct/Nov)
    elif rel_date.month in [10, 11]:
        s_market, s_seasonal = 90, 85

    # Apply Clash Penalty
    if inputs['has_clash']:
        s_market -= 15

    # 2. THE PREDICTABILITY EQUATION
    weighted_sum = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # Global Multipliers
    final_prob = weighted_sum * inputs['m_cert'] * inputs['m_align']
    final_prob = min(final_prob, 99.0)

    # 3. FINANCIAL LOGIC (Efficiency & ROI)[cite: 4]
    efficiency = 1.0
    if inputs['budget'] > 120 and s_talent < 90:
        efficiency = 0.7  # Penalty for high budget on non-veteran talent[cite: 4]
        
    market_cap = 450 # Scalable for future inflation
    rev_bonus = 1.4 if inputs['is_franchise'] else 1.0
    est_rev = (final_prob / 100) * market_cap * efficiency * rev_bonus
    roi = ((est_rev - inputs['budget']) / inputs['budget']) * 100

    return final_prob, est_rev, roi