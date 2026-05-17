
# news_fetcher.py — récupération et filtrage des news XAUUSD via NewsAPI
import requests
from config import NEWS_API_URL, NEWS_API_KEY# Mots-clés stricts XAUUSD
MACRO_KEYWORDS = [
    "gold", "xauusd", "xau/usd", "bullion", "gold price",
    "fed", "federal reserve", "fomc", "powell", "interest rate",
    "inflation", "cpi", "pce", "nonfarm", "payroll",
    "gdp", "treasury", "yield", "dollar index", "dxy",
    "geopolitical", "safe haven", "war", "conflict", "sanctions",
    "recession", "stagflation", "rate hike", "rate cut"
]

# Mots-clés à exclure (bruit)
EXCLUDE_KEYWORDS = [
    "fashion", "sport", "movie", "celebrity", "recipe",
    "tile", "bathroom", "football", "basketball", "nba",
    "nfl", "entertainment", "gaming", "makeup", "beauty"
]

def fetch_latest_news(limit=30):
    params = {
        "q": "gold price OR XAUUSD OR bullion OR 'federal reserve' OR 'interest rate' OR inflation",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title":       article.get("title", ""),
                "description": article.get("description", ""),
                "source":      article.get("source", {}).get("name", ""),
                "ts":          article.get("publishedAt", "")
            })
        return articles

    except Exception as e:
        print(f"Erreur NewsAPI : {e}")
        return []


def filter_macro_news(articles):
    filtered = []
    for article in articles:
        text = ((article["title"] or "") + " " + (article["description"] or "")).lower()
        
        # Exclure si mot-clé parasite détecté
        if any(ex in text for ex in EXCLUDE_KEYWORDS):
            continue
        
        # Garder uniquement si mot-clé macro présent
        if any(kw in text for kw in MACRO_KEYWORDS):
            filtered.append(article)

    return filtered