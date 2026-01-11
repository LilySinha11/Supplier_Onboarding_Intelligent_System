def analyze_financials(balance, income):

    current_ratio = balance["totalCurrentAssets"] / max(balance["totalCurrentLiabilities"],1)
    debt_to_equity = balance["totalDebt"] / max(balance["totalStockholdersEquity"],1)
    net_margin = income["netIncome"] / max(income["revenue"],1)

    risk = 0

    if current_ratio < 1:
        risk += 30
    if debt_to_equity > 2:
        risk += 30
    if net_margin < 0.05:
        risk += 20

    score = max(0, 100 - risk)

    if score > 75:
        decision = "APPROVE"
    elif score > 50:
        decision = "APPROVE_WITH_LIMIT"
    else:
        decision = "REJECT"

    return {
        "financial_score": score,
        "current_ratio": round(current_ratio,2),
        "debt_to_equity": round(debt_to_equity,2),
        "net_margin": round(net_margin,2),
        "credit_recommendation": decision
    }
