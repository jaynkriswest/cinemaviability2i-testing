# formula.py - Clde version
# Complete predictability calculation with proper ROI estimation

def calculate_v3i_logic(inputs):
    """
    Calculate predictability score, revenue estimate, and ROI.
    
    Args:
        inputs (dict): Dictionary with all scoring parameters
    
    Returns:
        tuple: (predictability_score, est_revenue, roi_percentage)
    """
    
    # =====================================================
    # STEP 1: EXTRACT INPUTS (with defaults for safety)
    # =====================================================
    
    s_talent = float(inputs.get('talent_score', 85))
    s_market_base = float(inputs.get('market_base', 85))
    s_market_multiplier = float(inputs.get('market_multiplier', 1.0))
    has_clash = inputs.get('has_clash', False)
    s_content = float(inputs.get('content_score', 80))
    s_viral = float(inputs.get('viral_score', 70))
    s_seasonal = float(inputs.get('seasonal_score', 80))
    m_cert = float(inputs.get('m_cert', 1.0))
    m_align = float(inputs.get('m_align', 0.95))
    budget = float(inputs.get('budget', 50.0))
    is_franchise = inputs.get('is_franchise', False)
    
    # Safety: ensure budget is positive
    if budget <= 0:
        budget = 50.0
    
    # =====================================================
    # STEP 2: PILLAR CALCULATIONS
    # =====================================================
    
    # Pillar 1: Talent (30%)
    # Already normalized to 0-100
    s_talent = max(0, min(100, s_talent))
    
    # Pillar 2: Market (20%)
    # Market = base score × seasonal/market multiplier
    s_market = (s_market_base * s_market_multiplier)
    
    # Apply clash penalty (major superstar clash reduces market score)
    if has_clash:
        s_market -= 15
    
    # Normalize market to 0-100
    s_market = max(0, min(100, s_market))
    
    # Pillar 3: Content (20%)
    # Franchise bonus: proven IP gets higher content score
    s_content = float(s_content)
    if is_franchise:
        s_content *= 1.4
    
    # Normalize content to 0-100
    s_content = max(0, min(100, s_content))
    
    # Pillar 4: Viral (15%)
    # Already normalized to 0-100
    s_viral = max(0, min(100, s_viral))
    
    # Pillar 5: Seasonal (15%)
    # Already normalized to 0-100
    s_seasonal = max(0, min(100, s_seasonal))
    
    # =====================================================
    # STEP 3: WEIGHTED SUM (Base Predictability)
    # =====================================================
    
    weighted_sum = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # =====================================================
    # STEP 4: APPLY GLOBAL MULTIPLIERS
    # =====================================================
    
    final_prob = weighted_sum * m_cert * m_align
    
    # Cap at 99% (realism constraint)
    final_prob = min(final_prob, 99.0)
    final_prob = max(final_prob, 10.0)  # Minimum floor
    
    # =====================================================
    # STEP 5: REVENUE & ROI CALCULATION
    # =====================================================
    
    # Efficiency multiplier based on talent and budget fit
    efficiency = 1.0
    
    # If budget > 150Cr AND talent < 90, apply efficiency penalty
    if budget > 150 and s_talent < 90:
        efficiency = 0.80
    
    # If budget > 100Cr but talent is strong, apply bonus
    if budget > 100 and s_talent >= 90:
        efficiency = 1.10
    
    # Base ROI multiplier: 2.0x (for 100% predictability, break even)
    # This means: revenue = budget × 2.0 × efficiency → profit = budget
    revenue_multiplier = 2.0
    
    # Adjust ROI multiplier based on talent tier
    if s_talent >= 95:
        revenue_multiplier = 2.5  # Ultra-Veterans perform 2.5x
    elif s_talent >= 85:
        revenue_multiplier = 2.2  # Veterans perform 2.2x
    elif s_talent >= 75:
        revenue_multiplier = 2.0  # Superstars perform 2.0x
    else:
        revenue_multiplier = 1.6  # Rising stars perform 1.6x
    
    # Calculate estimated gross revenue
    # Revenue = Budget × Revenue_Multiplier × (Predictability/100) × Efficiency
    confidence_factor = final_prob / 100.0
    est_revenue = (budget * revenue_multiplier * confidence_factor * efficiency)
    
    # =====================================================
    # STEP 6: ROI PERCENTAGE
    # =====================================================
    
    # ROI = (Revenue - Budget) / Budget × 100
    # But account for distribution costs (~35% of gross)
    distribution_cut = 0.35
    net_revenue = est_revenue * (1 - distribution_cut)
    
    # Marketing costs (~25% of budget for wide releases)
    marketing_cost = budget * 0.25
    
    # Total cost = production budget + marketing
    total_cost = budget + marketing_cost
    
    # Profit = net revenue - total cost
    profit = net_revenue - total_cost
    
    # ROI percentage
    roi = (profit / budget * 100) if budget > 0 else 0
    
    # Ensure ROI is not negative (cap at -100%)
    roi = max(roi, -100)
    
    return min(final_prob, 99.0), est_revenue, roi


def calculate_detailed_prediction(inputs):
    """
    Extended calculation with breakdown for producer dashboard.
    
    Returns:
        dict: Detailed prediction with all components
    """
    
    # Get base calculation
    prob, revenue, roi = calculate_v3i_logic(inputs)
    
    # Extract individual components for transparency
    s_talent = inputs.get('talent_score', 85)
    s_market = inputs.get('market_base', 85) * inputs.get('market_multiplier', 1.0)
    s_content = inputs.get('content_score', 80)
    s_viral = inputs.get('viral_score', 70)
    s_seasonal = inputs.get('seasonal_score', 80)
    
    # Calculate risk level
    if prob >= 90:
        risk_level = "Low Risk - Greenlight Recommended"
    elif prob >= 80:
        risk_level = "Medium Risk - Proceed with Caution"
    elif prob >= 70:
        risk_level = "High Risk - Major Concerns"
    else:
        risk_level = "Very High Risk - Not Recommended"
    
    # ROI scenarios
    budget = inputs.get('budget', 50)
    optimistic_roi = roi * 1.3
    pessimistic_roi = roi * 0.6
    
    return {
        'predictability_score': round(prob, 1),
        'risk_level': risk_level,
        'revenue_estimate': round(revenue, 1),
        'roi_percentage': round(roi, 1),
        'roi_optimistic': round(optimistic_roi, 1),
        'roi_pessimistic': round(pessimistic_roi, 1),
        'breakdown': {
            'talent': round(s_talent, 1),
            'market': round(s_market, 1),
            'content': round(s_content, 1),
            'viral': round(s_viral, 1),
            'seasonal': round(s_seasonal, 1),
        },
        'budget_crores': budget,
    }
