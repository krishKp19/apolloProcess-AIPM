def risk_score(flags):
    score = 0

    if "low_oxygen" in flags:
        score += 40
    if "cardiac_risk" in flags:
        score += 30
    if "tachycardia" in flags:
        score += 20

    return min(score, 100)