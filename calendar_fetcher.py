# calendar_fetcher.py — récupération du calendrier économique via Finnhub
import requests
from datetime import datetime, timedelta, timezone
from config import FINNHUB_API_KEY

IMPORTANT_EVENTS = [
    "fomc", "federal reserve", "cpi", "inflation", "nonfarm",
    "payroll", "gdp", "pce", "powell", "interest rate",
    "unemployment", "retail sales", "pmi", "ism"
]

def get_economic_calendar(days_ahead=7):
    """Récupère les événements économiques des X prochains jours"""

    now = datetime.now(timezone.utc)
    date_from = now.strftime("%Y-%m-%d")
    date_to = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    url = "https://finnhub.io/api/v1/calendar/economic"
    params = {
        "from": date_from,
        "to": date_to,
        "token": FINNHUB_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        events = []
        for event in data.get("economicCalendar", []):
            event_name = (event.get("event") or "").lower()

            if any(kw in event_name for kw in IMPORTANT_EVENTS):
                dt_str = event.get("time") or event.get("date")
                try:
                    if "T" in str(dt_str):
                        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                    else:
                        dt = datetime.strptime(dt_str, "%Y-%m-%d").replace(
                            tzinfo=timezone.utc
                        )
                except Exception:
                    continue

                events.append({
                    "name":     event.get("event", ""),
                    "country":  event.get("country", ""),
                    "impact":   event.get("impact", ""),
                    "datetime": dt,
                    "actual":   event.get("actual"),
                    "estimate": event.get("estimate"),
                    "previous": event.get("previous"),
                })

        events.sort(key=lambda x: x["datetime"])
        return events

    except Exception as e:
        print(f"Erreur Finnhub : {e}")
        return []


def get_imminent_events(events, hours=2):
    """Retourne les événements dans les X prochaines heures"""
    now = datetime.now(timezone.utc)
    return [
        e for e in events
        if timedelta(0) < (e["datetime"] - now) < timedelta(hours=hours)
    ]