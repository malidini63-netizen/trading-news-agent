# alerts.py — notifications Telegram
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram(message: str) -> bool:
    """Envoie un message Telegram au chat configuré"""

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram non configuré.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erreur Telegram : {e}")
        return False


def format_alert(result: dict, bias_result: dict) -> str:
    """Formate le message d'alerte pour Telegram"""

    bias_ia = result.get("bias", "N/A")
    confidence = result.get("confidence", "N/A")
    bias_final = bias_result.get("bias", "neutre").upper()
    score = bias_result.get("score", 0)
    trader_phrase = result.get("trader_phrase", "")
    summary = result.get("summary", "")

    # Emoji selon le biais
    if "haussier" in bias_final.lower():
        emoji = "📈"
    elif "baissier" in bias_final.lower():
        emoji = "📉"
    elif "prudence" in bias_final.lower():
        emoji = "⚠️"
    else:
        emoji = "➡️"

    # Événements imminents
    imminent_text = ""
    if bias_result.get("imminent"):
        imminent_text = "\n\n🚨 *ÉVÉNEMENT IMMINENT :*\n"
        for e in bias_result["imminent"]:
            imminent_text += f"- {e['name']}\n"

    # Événements à surveiller
    events_text = ""
    if result.get("events_to_watch"):
        events_text = "\n\n🔔 *À surveiller :*\n"
        for e in result["events_to_watch"]:
            events_text += f"- {e}\n"

    message = f"""🥇 *XAUUSD — Analyse Macro*

📋 *Résumé :*
{summary}

{emoji} *Biais final :* {bias_final}
🤖 *Biais IA :* {bias_ia}
📊 *Score :* {score}
🎯 *Confiance :* {confidence}

💬 *Phrase trader :*
_{trader_phrase}_{imminent_text}{events_text}"""

    return message