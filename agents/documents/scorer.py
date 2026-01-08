def compute_score(expired_docs, name_consistent):
    score = 1.0

    if expired_docs:
        score -= 0.3

    if not name_consistent:
        score -= 0.3

    return round(max(score, 0.0), 2)
