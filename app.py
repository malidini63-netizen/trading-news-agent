# app.py — dashboard pro avec graphiques
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timezone
from config import assert_config
from news_fetcher import fetch_latest_news, filter_macro_news
from analyzer import analyze_news
from bias_engine import compute_score
from calendar_fetcher import get_economic_calendar
from alerts import send_telegram, format_alert
from storage import save_entry, get_last_entries, clear_history

st.set_page_config(
    page_title="XAUUSD — Trading Agent",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #3a3a5e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 5px 0;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #f0c040;
    }
    .metric-label {
        font-size: 0.85em;
        color: #aaa;
        margin-top: 5px;
    }
    .news-card {
        background: linear-gradient(135deg, rgba(240, 192, 64, 0.08), rgba(255,255,255,0.03));
        border: 1px solid rgba(240, 192, 64, 0.3);
        border-left: 3px solid #f0c040;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 8px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .news-card:hover {
        background: linear-gradient(135deg, rgba(240, 192, 64, 0.12), rgba(255,255,255,0.05));
        box-shadow: 0 6px 28px rgba(240, 192, 64, 0.2);
    }
    .event-high { border-left: 3px solid #ff4b4b; }
    .event-med  { border-left: 3px solid #ffa500; }
    .event-low  { border-left: 3px solid #888; }
</style>
""", unsafe_allow_html=True)

assert_config()

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Gold_bullion_bars.jpg/320px-Gold_bullion_bars.jpg", width="stretch")
    st.title("⚙️ Paramètres")
    st.divider()

    interval = st.selectbox(
        "📅 Horizon calendrier",
        options=[3, 5, 7, 14],
        index=2,
        format_func=lambda x: f"{x} jours"
    )

    max_news = st.slider("📰 Nombre de news", 10, 50, 30, step=5)
    max_display = st.slider("📋 News affichées", 5, 15, 10)

    st.divider()
    st.caption("🤖 Modèle : Groq LLaMA 3")
    st.caption("📡 Source : NewsAPI + Finnhub")
    st.caption(f"🕐 {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}")

# ── HEADER ───────────────────────────────────────────────
st.markdown("# 🥇 XAUUSD — Trading News Agent")
st.caption("Analyse macro IA en temps réel • ICT/SMC bias engine")
st.divider()

# ── SESSION STATE ─────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "bias_result" not in st.session_state:
    st.session_state.bias_result = None

# ── BOUTON ANALYSE ────────────────────────────────────────
if st.button("🔍 Lancer l'analyse", type="primary", use_container_width=True):
    with st.spinner("📅 Calendrier économique..."):
        events = get_economic_calendar(days_ahead=interval)
    with st.spinner("📰 Récupération des news..."):
        raw = fetch_latest_news(limit=max_news)
        macro = filter_macro_news(raw)
    with st.spinner("🤖 Analyse IA en cours..."):
        st.session_state.result = analyze_news(macro)
        st.session_state.bias_result = compute_score(
            st.session_state.result, upcoming_events=events
        )
        st.session_state.events = events
        st.session_state.macro = macro
        save_entry(st.session_state.result, st.session_state.bias_result)

st.divider()

# ── AFFICHAGE RÉSULTATS ───────────────────────────────────
if st.session_state.result and st.session_state.bias_result:
    result = st.session_state.result
    bias_result = st.session_state.bias_result
    events = st.session_state.get("events", [])
    macro = st.session_state.get("macro", [])

    score = bias_result.get("score", 0)
    bias_final = bias_result.get("bias", "neutre")
    bias_ia = result.get("bias", "N/A")
    confidence = result.get("confidence", "N/A")

    # ── JAUGE SCORE ───────────────────────────────────────
    st.subheader("📊 Score de biais XAUUSD")

    gauge_color = "#26a269" if score > 0 else "#e01b24" if score < 0 else "#f0c040"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": 0, "valueformat": "+d"},
        gauge={
            "axis": {"range": [-5, 5], "tickwidth": 1},
            "bar": {"color": gauge_color},
            "steps": [
                {"range": [-5, -2], "color": "#3b0a0a"},
                {"range": [-2, -0.5], "color": "#5a1a1a"},
                {"range": [-0.5, 0.5], "color": "#2a2a2a"},
                {"range": [0.5, 2], "color": "#0a3b1a"},
                {"range": [2, 5], "color": "#0a5a1a"},
            ],
            "threshold": {
                "line": {"color": "#f0c040", "width": 3},
                "thickness": 0.75,
                "value": score
            }
        },
        title={"text": f"Biais final : {bias_final.upper()}", "font": {"size": 18}}
    ))
    fig_gauge.update_layout(
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"}
    )
    st.plotly_chart(fig_gauge, width="stretch")
    # ── MÉTRIQUES ─────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{bias_final.upper()}</div>
            <div class="metric-label">Biais Final</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{bias_ia}</div>
            <div class="metric-label">Biais IA</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{score:+d}</div>
            <div class="metric-label">Score</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{confidence}</div>
            <div class="metric-label">Confiance</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── CONTENU PRINCIPAL ─────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        # ── ANALYSE STRUCTURÉE ────────────────────────────
        st.subheader("🧠 Analyse macro IA")

        # Biais CT + Swing
        bct = result.get("biais_ct", "N/A").upper()
        bsw = result.get("biais_swing", "N/A").upper()
        col_ct, col_sw = st.columns(2)
        with col_ct:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="font-size:1.2em">{bct}</div>
                <div class="metric-label">🌍 Biais CT (intraday)</div>
                <div style="color:#ccc;font-size:0.8em;margin-top:6px">{result.get("biais_ct_justification","")}</div>
            </div>""", unsafe_allow_html=True)
        with col_sw:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="font-size:1.2em">{bsw}</div>
                <div class="metric-label">📈 Biais Swing (multi-jours)</div>
                <div style="color:#ccc;font-size:0.8em;margin-top:6px">{result.get("biais_swing_justification","")}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Session & Kill Zone
        session = result.get("session", "N/A")
        kz = result.get("kill_zone", "Aucune")
        st.markdown(f"🔎 **Session active :** {session} &nbsp;|&nbsp; **Kill Zone :** {kz}")

        st.divider()

        # News scorées
        news_an = result.get("news_analysees", [])
        if news_an:
            st.subheader("📰 News scorées")
            for n in news_an:
                direction = n.get("direction", "Neutre")
                intensite = n.get("intensite", "")
                color = "#26a269" if "XAU+" in direction or "USD-" in direction else \
                        "#e01b24" if "XAU-" in direction or "USD+" in direction else "#888"
                st.markdown(f"""<div class="news-card" style="border-left-color:{color}">
                    <strong>{n.get('titre','')}</strong><br>
                    <small style="color:{color}">▶ {direction}</small>
                    <small style="color:#aaa"> — {intensite}</small>
                </div>""", unsafe_allow_html=True)
        else:
            # fallback résumé texte
            st.subheader("🧠 Résumé IA")
            st.info(result.get("summary", ""))

        st.divider()

        # Catalyseurs
        if result.get("catalyseurs"):
            st.subheader("⚡ Catalyseurs clés")
            for c in result["catalyseurs"]:
                st.markdown(f"- {c}")

        # Alertes
        alertes = result.get("alertes", [])
        if alertes:
            st.subheader("⚠️ Alertes")
            for a in alertes:
                st.warning(a)

        # Alerte imminente (bias_engine)
        if bias_result.get("imminent"):
            st.error("🚨 ÉVÉNEMENT IMMINENT — Prudence !")
            for e in bias_result["imminent"]:
                st.markdown(f"- **{e['name']}** dans moins de 2h")

        # Remarque analyst
        if result.get("remarque_analyst"):
            st.subheader("💬 Remarque Analyst")
            st.info(result.get("remarque_analyst"))

        # Phrase trader
        st.subheader("💬 Phrase trader")
        st.success(result.get("trader_phrase", ""))

        # Événements à surveiller
        if result.get("events_to_watch"):
            st.subheader("🔔 Événements à surveiller")
            for e in result["events_to_watch"]:
                st.markdown(f"- {e}")

        st.divider()

        # Bouton Telegram
        alert_msg = format_alert(result, bias_result)
        if st.button("📱 Envoyer sur Telegram", type="secondary", use_container_width=True):
            with st.spinner("Envoi..."):
                success = send_telegram(alert_msg)
            if success:
                st.success("✅ Alerte envoyée !")
            else:
                st.error("❌ Échec envoi Telegram.")

        with st.expander("👁️ Aperçu message Telegram"):
            st.text(alert_msg)

    with col_right:
        # News filtrées
        st.subheader(f"📰 News macro ({len(macro)})")
        for n in macro[:max_display]:
            st.markdown(f"""<div class="news-card">
                <strong>{n['title']}</strong><br>
                <small style="color:#aaa">[{n['source']}] — {n['ts'][:10]}</small>
            </div>""", unsafe_allow_html=True)

        st.divider()

        # Calendrier économique
        st.subheader(f"📅 Calendrier ({interval} jours)")
        if not events:
            st.info("Aucun événement majeur trouvé.")
        else:
            for e in events[:8]:
                dt = e["datetime"].strftime("%d/%m %H:%M")
                impact = e.get("impact", "")
                css = "event-high" if impact == "high" else "event-med" if impact == "medium" else "event-low"
                emoji = "🔴" if impact == "high" else "🟡" if impact == "medium" else "⚪"
                st.markdown(f"""<div class="news-card {css}">
                    {emoji} <strong>{e['name']}</strong> — {dt} UTC<br>
                    <small style="color:#aaa">Estimé: {e.get('estimate','N/A')} | Préc: {e.get('previous','N/A')}</small>
                </div>""", unsafe_allow_html=True)

# ── GRAPHIQUE HISTORIQUE ──────────────────────────────────
st.divider()
st.subheader("📈 Historique des biais")

history = get_last_entries(20)

if len(history) >= 2:
    df = pd.DataFrame(history)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df.index = range(len(df))

    fig_hist = px.line(
        df,
        x="timestamp",
        y="score",
        markers=True,
        title="Évolution du score de biais XAUUSD",
        color_discrete_sequence=["#f0c040"]
    )
    fig_hist.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
    fig_hist.add_hrect(y0=1, y1=5, fillcolor="green", opacity=0.1)
    fig_hist.add_hrect(y0=-5, y1=-1, fillcolor="red", opacity=0.1)
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        xaxis={"gridcolor": "#333"},
        yaxis={"gridcolor": "#333", "range": [-5, 5]},
        height=300
    )
    st.plotly_chart(fig_hist, width="stretch")

elif history:
    st.info("Lance au moins 2 analyses pour voir le graphique historique.")

# Tableau historique
if history:
    if st.button("🗑️ Effacer l'historique"):
        clear_history()
        st.rerun()

    for entry in reversed(history[-10:]):
        bias = entry.get("bias_final", "neutre")
        emoji = "📈" if "haussier" in bias else "📉" if "baissier" in bias else "➡️"
        with st.expander(f"{emoji} {entry['timestamp']} — {bias.upper()} (score: {entry['score']})"):
            st.write(entry.get("summary", ""))
            st.markdown(f"**💬 Phrase trader :** {entry.get('trader_phrase', '')}")
else:
    st.info("Aucune analyse enregistrée pour l'instant.")