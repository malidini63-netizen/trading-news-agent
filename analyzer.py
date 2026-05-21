# analyzer.py — analyse des news via Groq IA
import json
from groq import Groq
from config import GROQ_API_KEY, AI_MODEL, SYSTEM_PROMPT

client = Groq(api_key=GROQ_API_KEY)

EMPTY_RESULT = {
    "news_analysees": [],
    "biais_ct": "neutre",
    "biais_ct_justification": "Aucune news disponible.",
    "biais_swing": "neutre",
    "biais_swing_justification": "Aucune news disponible.",
    "catalyseurs": [],
    "session": "N/A",
    "kill_zone": "Aucune",
    "alertes": [],
    "remarque_analyst": "Pas assez de données pour produire une analyse.",
    "summary": "Aucune news macro disponible.",
    "bias": "neutre",
    "confidence": "faible",
    "events_to_watch": [],
    "trader_phrase": "Pas assez de données pour trader.",
}


def analyze_news(articles: list) -> dict:
    """Envoie les news filtrées à l'IA et retourne un dict structuré."""

    if not articles:
        return EMPTY_RESULT

    # Préparer le texte des news
    news_text = ""
    for i, article in enumerate(articles[:15], 1):
        news_text += f"{i}. [{article['source']}] {article['title']}\n"
        if article.get("description"):
            news_text += f"   {article['description']}\n\n"

    user_prompt = f"""Voici les dernières news macro à analyser :

{news_text}

Réponds UNIQUEMENT en JSON valide, sans texte avant ou après.
Respecte scrupuleusement le format défini dans tes instructions."""

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1200,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()

        # Nettoyage si le modèle ajoute des backticks malgré tout
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        result = json.loads(content)

        # Garantir que tous les champs existent (rétrocompatibilité)
        for key, default in EMPTY_RESULT.items():
            result.setdefault(key, default)

        return result

    except json.JSONDecodeError:
        fallback = EMPTY_RESULT.copy()
        fallback["summary"] = content if "content" in dir() else "Erreur parsing JSON."
        fallback["remarque_analyst"] = "La réponse IA n'était pas du JSON valide."
        return fallback

    except Exception as e:
        fallback = EMPTY_RESULT.copy()
        fallback["summary"] = f"Erreur IA : {e}"
        return fallback