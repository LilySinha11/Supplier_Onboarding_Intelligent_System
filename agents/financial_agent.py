import os
from agents.financial.api_client import get_balance_sheet, get_income_statement


def run(state):
    # ----------------------------------
    # Stage setup
    # ----------------------------------
    state["current_stage"] = "financial"
    state["agent_logs"].append("💰 Starting Financial Health Evaluation")

    # ----------------------------------
    # Always initialize (CRITICAL)
    # ----------------------------------
    state.setdefault("financial_metrics", {})
    state.setdefault("financial_score", 0.0)
    state.setdefault("credit_recommendation", "UNKNOWN")

    supplier = (state.get("supplier_name") or "").strip().lower()

    # ----------------------------------
    # Company → Stock Symbol Map
    # ----------------------------------
    symbol_map = {
        "tata motors": "TTM",
        "infosys": "INFY",
        "wipro": "WIT",
        "hdfc": "HDB",
        "tcs": "TCS"
    }

    symbol = symbol_map.get(supplier)

    # ----------------------------------
    # If company not listed → safe exit
    # ----------------------------------
    if not symbol:
        state["financial_score"] = 0.5
        state["credit_recommendation"] = "MANUAL REVIEW"
        state["financial_metrics"] = {
            "note": "Company not publicly listed. Financial API not available."
        }
        state["workflow_status"] = "COMPLETED"

        state["agent_logs"].append(
            f"⚠ No stock symbol found for '{supplier}' → manual review"
        )

        return state

    # ----------------------------------
    # Financial API Calls
    # ----------------------------------
    try:
        balance = get_balance_sheet(symbol) or {}
        income = get_income_statement(symbol) or {}

        # ----------------------------------
        # SAFE numeric extraction
        # ----------------------------------
        total_assets = float(balance.get("totalAssets") or 1)
        total_liabilities = float(balance.get("totalLiabilities") or 1)
        revenue = float(income.get("revenue") or 1)
        net_income = float(income.get("netIncome") or 0)

        # ----------------------------------
        # Financial ratios
        # ----------------------------------
        debt_ratio = total_liabilities / total_assets
        profit_margin = net_income / revenue

        # ----------------------------------
        # Score (0–1)
        # ----------------------------------
        score = round((1 - debt_ratio) * 0.6 + profit_margin * 0.4, 2)

        if score >= 0.7:
            decision = "APPROVE"
        elif score >= 0.4:
            decision = "REVIEW"
        else:
            decision = "REJECT"

        # ----------------------------------
        # Store results
        # ----------------------------------
        state["financial_metrics"] = {
            "symbol": symbol,
            "debt_ratio": round(debt_ratio, 2),
            "profit_margin": round(profit_margin, 2),
            "revenue": revenue,
            "net_income": net_income
        }

        state["financial_score"] = score
        state["credit_recommendation"] = decision
        state["workflow_status"] = "COMPLETED"

        state["agent_logs"].append(
            f"✅ Financial analysis completed — Score={score}, Decision={decision}"
        )

        return state

    # ----------------------------------
    # API failure → fallback (never crash)
    # ----------------------------------
    except Exception as e:
        state["financial_score"] = 0.4
        state["credit_recommendation"] = "REVIEW"
        state["financial_metrics"] = {
            "error": str(e)
        }
        state["workflow_status"] = "COMPLETED"

        state["agent_logs"].append(
            f"❌ Financial API error — fallback used: {str(e)}"
        )

        return state
