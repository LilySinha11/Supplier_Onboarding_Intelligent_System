import feedparser

def fetch_from_google_rss(query: str):
    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    feed = feedparser.parse(rss_url)
    articles = []

    for entry in feed.entries[:5]:
        articles.append({
            "title": entry.title,
            "description": entry.summary if "summary" in entry else "",
            "source": "Google News",
            "url": entry.link
        })

    return articles
