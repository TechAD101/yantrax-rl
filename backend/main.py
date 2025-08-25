from flask import Flask, jsonify, request
from flask_cors import CORS
from services.notification_service import send_notification
from services.logger_service import logger, get_logs, log_message
from ai_agents.macro_monk import macro_monk_decision
from ai_agents.the_ghost import ghost_signal_handler
from ai_agents.data_whisperer import analyze_data
from ai_agents.degen_auditor import audit_trade
from rl_core.rl_trainer import train_model, run_rl_cycle
from rl_core.env_market_sim import MarketSimEnv
import sqlite3
import os
from datetime import datetime

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)
CORS(app)  # Allow frontend access

# -----------------------------
# DB Helper
# -----------------------------
def init_db():
    conn = sqlite3.connect("trade_journal.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            timestamp TEXT,
            signal TEXT,
            audit TEXT,
            reward REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_commentary (
            timestamp TEXT,
            agent TEXT,
            comment TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_to_journal(signal, audit, reward):
    conn = sqlite3.connect("trade_journal.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO journal_entries (timestamp, signal, audit, reward)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), signal, audit, reward))
    conn.commit()
    conn.close()

# -----------------------------
# Endpoints
# -----------------------------
@app.route("/")
def index():
    return jsonify({"message": "Yantra X RL Backend is Live 🚀"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Backend is alive"}), 200

@app.route("/logs", methods=["GET"])
def logs():
    return jsonify({"logs": get_logs()}), 200

@app.route("/notify", methods=["POST"])
def notify():
    data = request.get_json(force=True)
    message = data.get("message", "No message")
    subject = data.get("subject", "Yantra X Notification")
    to_email = data.get("to_email", os.getenv("SMTP_USER", ""))

    send_notification(subject, message, to_email)
    log_message(f"[Notify] {message}")
    return jsonify({"status": "sent", "message": message}), 200

# ---- Agent Cycle ----
@app.route("/run-cycle", methods=["POST"])
def run_cycle():
    try:
        market_data = analyze_data()
        logger.info(f"[Data Whisperer] Market data: {market_data}")

        strategy = macro_monk_decision(market_data)
        logger.info(f"[Macro Monk] Strategy: {strategy}")

        signal = ghost_signal_handler(strategy)
        logger.info(f"[The Ghost] Signal: {signal}")

        audit = audit_trade(signal)
        logger.info(f"[Degen Auditor] Audit: {audit}")

        env = MarketSimEnv()
        state, reward, done = env.step(signal)

        send_notification(
            subject="Yantra X Trade Cycle",
            message=f"Signal: {signal} | Audit: {audit} | Reward: {reward}",
            to_email=os.getenv("SMTP_USER", "")
        )

        log_to_journal(signal, audit, reward)
        logger.info(f"[Journal] Ep {state['cycle']}: Signal={signal}, Audit={audit}, Reward={reward}")

        return jsonify({
            "status": "success",
            "signal": signal,
            "audit": audit,
            "reward": reward,
            "state": state
        })

    except Exception as e:
        logger.error(f"Error during cycle: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ---- RL Training ----
@app.route("/train", methods=["POST"])
def trigger_training():
    result = train_model()
    return jsonify(result)

# ---- RL GOD Cycle ----
@app.route("/god-cycle", methods=["GET"])
def run_god_cycle():
    try:
        result = run_rl_cycle()
        return jsonify(result)
    except Exception as e:
        logger.error(f"RL Cycle error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ---- Journal ----
@app.route("/journal", methods=["GET"])
def view_journal():
    conn = sqlite3.connect("trade_journal.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM journal_entries ORDER BY timestamp DESC LIMIT 100")
    entries = cursor.fetchall()
    conn.close()

    journal_list = [
        {"timestamp": row[0], "signal": row[1], "audit": row[2], "reward": row[3]}
        for row in entries
    ]
    return jsonify(journal_list)

@app.route("/replay", methods=["GET"])
def replay_journal():
    conn = sqlite3.connect("trade_journal.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM journal_entries ORDER BY timestamp ASC")
    entries = cursor.fetchall()
    conn.close()

    replay = []
    for row in entries:
        timestamp, signal, audit, reward = row
        logger.info(f"[REPLAY] {timestamp} | Signal: {signal} | Audit: {audit} | Reward: {reward}")
        replay.append({
            "timestamp": timestamp,
            "signal": signal,
            "audit": audit,
            "reward": reward
        })
    return jsonify({"replay": replay})

@app.route("/commentary", methods=["GET"])
def get_agent_commentary():
    conn = sqlite3.connect("trade_journal.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_commentary ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {"timestamp": row[0], "agent": row[1], "comment": row[2]}
        for row in rows
    ])

# ---- Market Stats ----
@app.route("/market_stats", methods=["GET"])
def market_stats():
    symbol = request.args.get("symbol", "AAPL")
    market_data = analyze_data(symbol)
    return jsonify({"symbol": symbol, "market_data": market_data})

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    init_db()
    logger.info("Yantra X RL backend started ✅")
    app.run(debug=True, host="0.0.0.0", port=5000)
