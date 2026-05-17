# storage.py — sauvegarde locale de l'historique des biais
import json
import os
from datetime import datetime, timezone

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")


def load_history() -> list:
    """Charge l'historique depuis le fichier JSON"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur chargement historique : {e}")
        return []


def save_entry(result: dict, bias_result: dict) -> bool:
    """Sauvegarde une nouvelle entrée dans l'historique"""
    history = load_history()

    entry = {
        "timestamp":    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "bias_ia":      result.get("bias", "N/A"),
        "confidence":   result.get("confidence", "N/A"),
        "bias_final":   bias_result.get("bias", "N/A"),
        "score":        bias_result.get("score", 0),
        "trader_phrase": result.get("trader_phrase", ""),
        "summary":      result.get("summary", ""),
        "events":       result.get("events_to_watch", [])
    }

    history.append(entry)

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde : {e}")
        return False


def get_last_entries(n: int = 10) -> list:
    """Retourne les N dernières entrées"""
    history = load_history()
    return history[-n:]


def clear_history() -> bool:
    """Efface tout l'historique"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return True
    except Exception as e:
        print(f"Erreur suppression : {e}")
        return False