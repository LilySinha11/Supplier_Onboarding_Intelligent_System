import requests
import os

NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

def fetch_from_newsapi(query: str):
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&"
        f"language=en&"
        f"sortBy=publishedAt&"
        f"pageSize=5&"
        f"apiKey={NEWS_API_KEY}"
    )

    response = requests.get(url, timeout=5)
    data = response.json()

    articles = []

    for a in data.get("articles", []):
        articles.append({
            "title": a.get("title"),
            "description": a.get("description"),
            "source": "NewsAPI",
            "url": a.get("url")
        })

    return articles
