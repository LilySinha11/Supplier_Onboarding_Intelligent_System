def detect_event(state):
    if state["risk_score"] > 0.8:
        return {
            "reenter": True,
            "stage": "risk",
            "reason": "New negative news"
        }
    return None
