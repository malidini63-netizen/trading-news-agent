# scheduler.py — lancement automatique des analyses
import schedule
import time
import json
from datetime import datetime, timezone
from news_fetcher import fetch_latest_news, filter_macro_news
from analyzer import analyze_news
from bias_engine import compute_score
from calendar_fetcher import get_economic_calendar
from alerts import send_telegram, format_alert
from storage import save_entry

def run_analysis():
    """Lance une analyse complète et envoie l'alerte Telegram"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n[{now}] Lancement analyse automatique...")

    try:
        # 1. Calendrier
        events = get_economic_calendar(days_ahead=7)
        print(f"  ✅ {len(events)} événements récupérés")

        # 2. News
        raw = fetch_latest_news(limit=30)
        macro = filter_macro_news(raw)
        print(f"  ✅ {len(macro)} news macro filtrées")

        # 3. Analyse IA
        result = analyze_news(macro)
        bias_result = compute_score(result, upcoming_events=events)
        print(f"  ✅ Biais : {bias_result.get('bias')} (score: {bias_result.get('score')})")

        # 4. Sauvegarde
        save_entry(result, bias_result)
        print(f"  ✅ Analyse sauvegardée")

        # 5. Alerte Telegram
        alert_msg = format_alert(result, bias_result)
        sent = send_telegram(alert_msg)
        print(f"  ✅ Telegram : {'envoyé' if sent else 'échec'}")

    except Exception as e:
        print(f"  ❌ Erreur : {e}")
        send_telegram(f"⚠️ Erreur analyse automatique :\n{e}")


def start_scheduler(interval_hours=4):
    """Lance le scheduler — analyse toutes les X heures"""
    print(f"🚀 Scheduler démarré — analyse toutes les {interval_hours}h")
    print("   Appuie sur Ctrl+C pour arrêter\n")

    # Première analyse immédiate
    run_analysis()

    # Planification
    schedule.every(interval_hours).hours.do(run_analysis)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler(interval_hours=4)