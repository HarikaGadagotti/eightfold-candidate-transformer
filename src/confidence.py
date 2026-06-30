SOURCE_RELIABILITY = {
    "ats_json": 0.9,
    "recruiter_csv": 0.75,
    "github": 0.8,
    "resume": 0.65,
}

def field_confidence(source, num_corroborating=0):
    base = SOURCE_RELIABILITY.get(source, 0.5)
    score = base * (1 + 0.15 * num_corroborating)
    return round(min(score, 1.0), 2)