# bias_engine.py — calcul du score et biais final XAUUSD
from datetime import datetime, timedelta, timezone
from calendar_fetcher import get_economic_calendar, get_imminent_events


def compute_score(analysis: dict, upcoming_events: list = None) -> dict:

    if upcoming_events is None:
        upcoming_events = get_economic_calendar(days_ahead=7)

    score = 0

    # Impact USD depuis l'analyse IA
    impact_usd = analysis.get("impact_usd", "neutre")
    if impact_usd == "baissier":
        score += 1
    elif impact_usd == "haussier":
        score -= 1

    # Inférer depuis le résumé
    summary_low = (analysis.get("summary") or "").lower()
    if "rendements" in summary_low and "baisse" in summary_low:
        score += 1
    if "rendements" in summary_low and "hausse" in summary_low:
        score -= 1
    if "risk-off" in summary_low or "fuite" in summary_low:
        score += 1
    if "risk-on" in summary_low or "appétit" in summary_low:
        score -= 1

    # Override : événement majeur imminent (< 2h)
    imminent = get_imminent_events(upcoming_events, hours=2)
    if imminent:
        return {
            "score": score,
            "bias": "prudence",
            "reason": f"⚠️ Événement imminent : {imminent[0]['name']}",
            "events": upcoming_events,
            "imminent": imminent
        }

    # Calcul du biais final
    if score >= 3:
        bias = "haussier fort"
    elif score >= 1:
        bias = "haussier léger"
    elif score == 0:
        bias = "neutre"
    elif score >= -2:
        bias = "baissier léger"
    else:
        bias = "baissier fort"

    return {
        "score": score,
        "bias": bias,
        "reason": "",
        "events": upcoming_events,
        "imminent": imminent
    }