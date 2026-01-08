import os
from groq import Groq

from agents.news_sources import fetch_all_news


# --------------------------------------------------
# Safety check (fail fast, clear error)
# --------------------------------------------------
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY not found. "
        "Ensure .env is loaded before importing risk_agent."
    )


# --------------------------------------------------
# Groq Client
# --------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --------------------------------------------------
# Groq-based risk analysis
# --------------------------------------------------
def analyze_risk_with_groq(news_text: str):
    prompt = f"""
You are a supply chain risk analyst.

Based on the news below, assess supplier risk.

Respond STRICTLY in this format:
RISK_SCORE: <number between 0 and 1>
RISK_LEVEL: LOW | MEDIUM | HIGH
EXPLANATION: <short explanation>

News:
{news_text}
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = completion.choices[0].message.content.strip()
    lines = content.splitlines()

    score = float(lines[0].split(":")[1].strip())
    level = lines[1].split(":")[1].strip()
    explanation = lines[2].split(":", 1)[1].strip()

    return score, level, explanation


# --------------------------------------------------
# LangGraph Agent Entry Point
# --------------------------------------------------
def run(state):
    state["current_stage"] = "risk"
    state["agent_logs"].append("Starting risk intelligence agent")

    # 1️⃣ Fetch news from multiple sources
    articles = fetch_all_news(state["supplier_name"])

    if not articles:
        state["risk_score"] = 0.1
        state["risk_level"] = "LOW"
        state["risk_explanation"] = (
            "No adverse news found across multiple news sources"
        )
        state["risk_sources"] = []
        state["agent_logs"].append(
            "No news found across all configured sources"
        )
        return state

    # 2️⃣ Combine news text for LLM
    combined_text = " ".join(
        f"{a['title']}. {a.get('description', '')}"
        for a in articles
        if a.get("title")
    )

    sources = [a["url"] for a in articles if a.get("url")]

    # 3️⃣ Analyze risk using Groq
    score, level, explanation = analyze_risk_with_groq(combined_text)

    # 4️⃣ Update state
    state["risk_score"] = round(score, 2)
    state["risk_level"] = level
    state["risk_explanation"] = explanation
    state["risk_sources"] = sources

    state["agent_logs"].append(
        f"Risk assessed as {level} (score={state['risk_score']})"
    )

    return state
