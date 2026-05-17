# analyzer.py — analyse des news via Groq IA
import json
from groq import Groq
from config import GROQ_API_KEY, AI_MODEL

client = Groq(api_key=GROQ_API_KEY)

def analyze_news(articles):
    """Envoie les news filtrées à l'IA et retourne un dict structuré"""

    if not articles:
        return {
            "summary": "Aucune news macro disponible.",
            "bias": "NEUTRE",
            "confidence": "Faible",
            "trader_phrase": "Pas assez de données pour trader.",
            "events_to_watch": []
        }

    # Préparer le texte des news
    news_text = ""
    for i, article in enumerate(articles[:15], 1):
        news_text += f"{i}. [{article['source']}] {article['title']}\n"
        if article['description']:
            news_text += f"   {article['description']}\n\n"

    prompt = f"""Tu es un analyste expert en trading sur XAUUSD (Or).

Voici les dernières news macro :

{news_text}

Réponds UNIQUEMENT en JSON valide avec cette structure exacte :
{{
  "summary": "Résumé concis des éléments clés (3-4 phrases)",
  "bias": "HAUSSIER ou BAISSIER ou NEUTRE",
  "confidence": "Faible ou Moyen ou Élevé",
  "trader_phrase": "Une phrase d'action concrète pour le trader",
  "events_to_watch": ["événement 1", "événement 2", "événement 3"]
}}

Réponds en français. Ne mets rien avant ou après le JSON."""

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except json.JSONDecodeError:
        return {
            "summary": content,
            "bias": "N/A",
            "confidence": "N/A",
            "trader_phrase": "",
            "events_to_watch": []
        }
    except Exception as e:
        return {
            "summary": f"Erreur IA : {e}",
            "bias": "N/A",
            "confidence": "N/A",
            "trader_phrase": "",
            "events_to_watch": []
        }