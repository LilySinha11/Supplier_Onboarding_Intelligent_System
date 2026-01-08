from agents.news_sources.newsapi_source import fetch_from_newsapi
from agents.news_sources.google_rss_source import fetch_from_google_rss
from agents.news_sources.gdelt_source import fetch_from_gdelt

def fetch_all_news(query: str):
    articles = []

    try:
        articles.extend(fetch_from_newsapi(query))
    except:
        pass

    try:
        articles.extend(fetch_from_google_rss(query))
    except:
        pass

    try:
        articles.extend(fetch_from_gdelt(query))
    except:
        pass

    return articles
