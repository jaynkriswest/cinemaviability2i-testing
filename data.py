# data.py
# Categorized based on Pillar 1: Talent (30% Weight)
SOUTH_INDIAN_TALENT_DB = {
    "Chiranjeevi": {"score": 98, "category": "Ultra-Veteran"},
    "Rajinikanth": {"score": 98, "category": "Ultra-Veteran"},
    "Mammootty": {"score": 96, "category": "Ultra-Veteran"},
    "Prabhas": {"score": 94, "category": "Superstar"},
    "Allu Arjun": {"score": 93, "category": "Superstar"},
    "Siddu Jonnalagadda": {"score": 72, "category": "Rising Star"}
}

# Categorized based on Pillar 3: Content (20% Weight)
GENRE_BASELINES = {
    "Mass Action": 95, # High ROI
    "Family Drama": 85,
    "Mythological": 90,
    "Romance": 75,
    "Sci-Fi": 65      # High Risk
}

def get_talent_weight(name):
    return SOUTH_INDIAN_TALENT_DB.get(name, {"score": 60, "category": "Rising Star"})[cite: 10]