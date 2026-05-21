# alerts.py
import os
import requests
from datetime import datetime, timezone


def send_telegram(message: str) -> bool:
    """Envoie un message sur Telegram via le bot configuré."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def format_alert(result: dict, bias_result: dict) -> str:
    """Formate le message Telegram avec les nouveaux champs structurés."""

    now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    # ── Biais & score ─────────────────────────────────────
    bias_final = bias_result.get("bias", "neutre").upper()
    score = bias_result.get("score", 0)
    confidence = result.get("confidence", "N/A")

    emoji_bias = "📈" if "HAUSSIER" in bias_final else "📉" if "BAISSIER" in bias_final else "⚠️" if "PRUDENCE" in bias_final else "➡️"

    # ── Biais CT / Swing ──────────────────────────────────
    biais_ct = result.get("biais_ct", "N/A").upper()
    biais_ct_just = result.get("biais_ct_justification", "")
    biais_swing = result.get("biais_swing", "N/A").upper()
    biais_swing_just = result.get("biais_swing_justification", "")

    # ── Session & Kill Zone ───────────────────────────────
    session = result.get("session", "N/A")
    kill_zone = result.get("kill_zone", "Aucune")

    # ── News scorées ──────────────────────────────────────
    news_an = result.get("news_analysees", [])
    news_lines = ""
    for n in news_an:
        direction = n.get("direction", "Neutre")
        intensite = n.get("intensite", "")
        titre = n.get("titre", "")
        arrow = "🟢" if "XAU+" in direction or "USD-" in direction else \
                "🔴" if "XAU-" in direction or "USD+" in direction else "⚪"
        news_lines += f"  {arrow} {titre[:60]} — *{direction}* ({intensite})\n"

    if not news_lines:
        news_lines = f"  {result.get('summary', 'N/A')}"

    # ── Catalyseurs ───────────────────────────────────────
    catalyseurs = result.get("catalyseurs", [])
    cat_lines = "\n".join([f"  • {c}" for c in catalyseurs]) if catalyseurs else "  N/A"

    # ── Alertes ───────────────────────────────────────────
    alertes = result.get("alertes", [])
    imminent = bias_result.get("imminent", [])

    alerte_lines = ""
    for a in alertes:
        alerte_lines += f"  ⚠️ {a}\n"
    for e in imminent:
        alerte_lines += f"  🚨 IMMINENT : {e.get('name','')} dans < 2h\n"
    if not alerte_lines:
        alerte_lines = "  Aucune alerte"

    # ── Remarque analyst ──────────────────────────────────
    remarque = result.get("remarque_analyst", "")

    # ── Phrase trader ─────────────────────────────────────
    trader_phrase = result.get("trader_phrase", "")

    # ── Événements à surveiller ───────────────────────────
    events_to_watch = result.get("events_to_watch", [])
    events_lines = "\n".join([f"  • {e}" for e in events_to_watch]) if events_to_watch else "  Aucun"

    # ── Assemblage du message ─────────────────────────────
    message = f"""🥇 *XAUUSD — Trading News Agent*
🕐 {now}

━━━━━━━━━━━━━━━━━━━━━━
{emoji_bias} *BIAIS FINAL : {bias_final}*
📊 Score : `{score:+d}` | Confiance : {confidence}
━━━━━━━━━━━━━━━━━━━━━━

🌍 *Biais CT (intraday) : {biais_ct}*
_{biais_ct_just}_

📈 *Biais Swing : {biais_swing}*
_{biais_swing_just}_

━━━━━━━━━━━━━━━━━━━━━━
🔎 *Session :* {session} | *Kill Zone :* {kill_zone}
━━━━━━━━━━━━━━━━━━━━━━

📰 *News scorées :*
{news_lines}
⚡ *Catalyseurs clés :*
{cat_lines}

⚠️ *Alertes :*
{alerte_lines}
🔔 *Événements à surveiller :*
{events_lines}

💬 *Remarque Analyst :*
_{remarque}_

✅ *{trader_phrase}*

━━━━━━━━━━━━━━━━━━━━━━
_Analyse automatique — Pas un conseil financier_"""

    return message