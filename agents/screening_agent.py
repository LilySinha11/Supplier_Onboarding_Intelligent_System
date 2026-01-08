import requests

# ---------- CONFIG ----------
BANNED_COUNTRIES = ["Iran", "North Korea"]
ALLOWED_CATEGORIES = ["IT", "FMCG", "Manufacturing"]

# ---------- HELPERS ----------
def check_company_website(company_name: str) -> bool:
    """
    Simple website existence check
    """
    domain = company_name.replace(" ", "").lower()
    url = f"https://www.{domain}.com"

    try:
        r = requests.get(url, timeout=3)
        return r.status_code == 200
    except:
        return False


def check_linkedin_presence(company_name: str) -> bool:
    """
    LinkedIn presence heuristic (no scraping)
    """
    slug = company_name.replace(" ", "-").lower()
    url = f"https://www.linkedin.com/company/{slug}"

    try:
        r = requests.get(url, timeout=3)
        return r.status_code in [200, 999]  # LinkedIn blocks often
    except:
        return False


# ---------- MAIN AGENT ----------
def run(state):
    logs = []
    score = 0.0

    state["current_stage"] = "screening"
    state["workflow_status"] = "RUNNING"

    # 1️⃣ Country eligibility
    if state["country"] in BANNED_COUNTRIES:
        state["screening_status"] = "REJECTED"
        state["pre_qualification_score"] = 0.0
        logs.append("Rejected: supplier from banned country")
        state["agent_logs"].extend(logs)
        state["workflow_status"] = "COMPLETED"
        return state
    score += 0.3
    logs.append("Country check passed")

    # 2️⃣ Category eligibility
    if state["category"] in ALLOWED_CATEGORIES:
        score += 0.3
        logs.append("Allowed category")
    else:
        score += 0.1
        logs.append("Category not preferred")

    # 3️⃣ Website existence
    if check_company_website(state["supplier_name"]):
        score += 0.2
        logs.append("Company website found")
    else:
        logs.append("Company website not found")

    # 4️⃣ LinkedIn presence
    if check_linkedin_presence(state["supplier_name"]):
        score += 0.2
        logs.append("LinkedIn presence detected")
    else:
        logs.append("LinkedIn presence not detected")

    # 5️⃣ Final decision
    score = round(score, 2)
    state["pre_qualification_score"] = score

    if score >= 0.7:
        state["screening_status"] = "PASSED"
    elif score >= 0.4:
        state["screening_status"] = "NEEDS_REVIEW"
    else:
        state["screening_status"] = "REJECTED"

    logs.append(f"Final screening decision: {state['screening_status']}")
    logs.append(f"Pre-qualification score: {score}")

    state["agent_logs"].extend(logs)

    # Move to next stage if passed
    if state["screening_status"] == "PASSED":
        state["current_stage"] = "risk"
    else:
        state["workflow_status"] = "COMPLETED"

    return state
