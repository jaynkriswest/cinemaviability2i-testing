SOUTH_INDIAN_TALENT_DB = {
    "Chiranjeevi": {"score": 96, "category": "Ultra-Veteran"},
    "Venkatesh": {"score": 94, "category": "Ultra-Veteran"},
    "Prabhas": {"score": 98, "category": "Pan-India Superstar"},
    "Allu Arjun": {"score": 97, "category": "Pan-India Superstar"},
    "Mahesh Babu": {"score": 95, "category": "Superstar"},
    "NTR Jr": {"score": 96, "category": "Superstar"}
}

def get_talent_weight(name):
    # Returns the score if found, otherwise returns a baseline "Rising Star" score
    return SOUTH_INDIAN_TALENT_DB.get(name, {"score": 70, "category": "Rising Star"})