# data.py - Clde version
# Complete South Indian Cinema Database with Genre Metrics

GENRE_METRICS = {
    "Action": {
        "base_score": 95,
        "risk": "Low",
        "roi_multiplier": 2.8,
        "seasonal_boost": {"Jan": 1.3, "Apr": 1.2, "Oct": 1.3, "Dec": 1.2}
    },
    "Drama": {
        "base_score": 80,
        "risk": "Moderate",
        "roi_multiplier": 1.9,
        "seasonal_boost": {"Jan": 0.9, "Apr": 0.95, "Jul": 1.1, "Oct": 1.0}
    },
    "Thriller": {
        "base_score": 82,
        "risk": "Moderate",
        "roi_multiplier": 2.4,
        "seasonal_boost": {"Jul": 1.2, "Aug": 1.15, "Sep": 1.1}
    },
    "Comedy": {
        "base_score": 75,
        "risk": "Moderate-High",
        "roi_multiplier": 1.8,
        "seasonal_boost": {"Apr": 1.1, "Oct": 1.2, "Dec": 1.3}
    },
    "Romance": {
        "base_score": 70,
        "risk": "High",
        "roi_multiplier": 1.6,
        "seasonal_boost": {"Feb": 1.2, "Jun": 1.1, "Dec": 1.15}
    },
    "Family": {
        "base_score": 78,
        "risk": "Moderate",
        "roi_multiplier": 2.3,
        "seasonal_boost": {"Apr": 1.2, "May": 1.2, "Dec": 1.4, "Jan": 1.3}
    },
    "Sci-Fi": {
        "base_score": 75,
        "risk": "High",
        "roi_multiplier": 2.1,
        "seasonal_boost": {"May": 1.1, "Jun": 1.15, "Dec": 1.2}
    },
}

TALENT_TIERS = {
    "Ultra-Veteran": {
        "score": 96,
        "min_credits": 200,
        "consistency": 0.92,
        "box_office_multiplier": 1.35
    },
    "Veteran": {
        "score": 88,
        "min_credits": 100,
        "consistency": 0.88,
        "box_office_multiplier": 1.25
    },
    "Superstar": {
        "score": 85,
        "min_credits": 50,
        "consistency": 0.85,
        "box_office_multiplier": 1.15
    },
    "Rising Star": {
        "score": 65,
        "min_credits": 10,
        "consistency": 0.65,
        "box_office_multiplier": 0.95
    }
}

# Real talent scores (curated database for South Indian cinema)
SOUTH_INDIAN_ACTORS = {
    "chiranjeevi": {
        "tier": "Ultra-Veteran",
        "score": 96,
        "industry": "Telugu",
        "recent_hits": ["Acharya", "Waltair Veerayya"]
    },
    "rajinikanth": {
        "tier": "Ultra-Veteran",
        "score": 98,
        "industry": "Tamil",
        "recent_hits": ["Jailer", "Lal Salaam"]
    },
    "prabhas": {
        "tier": "Superstar",
        "score": 90,
        "industry": "Telugu",
        "recent_hits": ["Radhe Shyam", "Saaho", "Project K"]
    },
    "allu_arjun": {
        "tier": "Superstar",
        "score": 88,
        "industry": "Telugu",
        "recent_hits": ["Pushpa", "Pushpa 2"]
    },
    "ram_charan": {
        "tier": "Superstar",
        "score": 87,
        "industry": "Telugu",
        "recent_hits": ["RRR", "Acharya", "Game Changer"]
    },
    "jr_ntr": {
        "tier": "Superstar",
        "score": 89,
        "industry": "Telugu",
        "recent_hits": ["RRR", "NTR 30"]
    },
    "vijay": {
        "tier": "Superstar",
        "score": 91,
        "industry": "Tamil",
        "recent_hits": ["Varisu", "Thalapathy 67"]
    },
    "ajith_kumar": {
        "tier": "Superstar",
        "score": 89,
        "industry": "Tamil",
        "recent_hits": ["Thunivu", "Goodfellas"]
    },
    "balakrishna": {
        "tier": "Veteran",
        "score": 88,
        "industry": "Telugu",
        "recent_hits": ["Veera Simha Reddy", "Akhanda"]
    },
    "suriya": {
        "tier": "Veteran",
        "score": 86,
        "industry": "Tamil",
        "recent_hits": ["Etharkkum Thunindhavan"]
    },
    "kamal_haasan": {
        "tier": "Veteran",
        "score": 90,
        "industry": "Tamil",
        "recent_hits": ["Vikram", "Sabaash Chandru"]
    },
}

DIRECTORS = {
    "rajamouli": {
        "tier": "Ultra-Veteran",
        "score": 97,
        "specialty": "Epic Action"
    },
    "sukumar": {
        "tier": "Veteran",
        "score": 88,
        "specialty": "Action/Drama"
    },
    "lokesh_kanagaraj": {
        "tier": "Veteran",
        "score": 85,
        "specialty": "Thriller"
    },
    "trivikram_srinivas": {
        "tier": "Veteran",
        "score": 84,
        "specialty": "Mass Entertainment"
    },
}

# Seasonal multipliers by month
SEASONAL_MULTIPLIERS = {
    1: 1.30,   # January (Sankranti peak)
    2: 0.95,   # February (Valentine's period)
    3: 0.90,   # March
    4: 1.20,   # April (Summer start)
    5: 1.15,   # May (Summer holidays)
    6: 1.10,   # June
    7: 0.85,   # July (Monsoon)
    8: 0.85,   # August
    9: 0.90,   # September
    10: 1.25,  # October (Dussehra)
    11: 1.25,  # November (Diwali prep)
    12: 1.30,  # December (Year-end holidays)
}

# Production house multipliers
PRODUCTION_HOUSES = {
    "mythri movie makers": 1.15,
    "hombale films": 1.12,
    "sri venkateswara creations": 1.10,
    "sithara entertainments": 1.08,
    "pvp cinema": 1.10,
    "bhadrakali pictures": 1.05,
}