import requests

def fetch_from_gdelt(query: str):
    url = (
        "https://api.gdeltproject.org/api/v2/doc/doc?"
        f"query={query}&"
        "mode=artlist&"
        "format=json&"
        "maxrecords=5"
    )

    response = requests.get(url, timeout=5)
    data = response.json()

    articles = []

    for a in data.get("articles", []):
        articles.append({
            "title": a.get("title"),
            "description": "",
            "source": "GDELT",
            "url": a.get("url")
        })

    return articles
