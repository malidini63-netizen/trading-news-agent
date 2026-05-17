# config.py — chargement et validation des variables d'environnement
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

NEWS_API_URL = os.getenv("NEWS_API_URL")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AI_MODEL     = os.getenv("AI_MODEL")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

def assert_config():
    """Vérifie que toutes les variables critiques sont présentes"""
    missing = [
        k for k, v in {
            "NEWS_API_URL": NEWS_API_URL,
            "NEWS_API_KEY": NEWS_API_KEY,
            "GROQ_API_KEY": GROQ_API_KEY,
            "AI_MODEL":     AI_MODEL,
            "FINNHUB_API_KEY": FINNHUB_API_KEY,
            "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
            "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        }.items() if not v
    ]
    if missing:
        raise RuntimeError(
            f"❌ Variables manquantes dans .env : {missing}"
        )