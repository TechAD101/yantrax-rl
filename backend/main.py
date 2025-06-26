# main.py — RL-enhanced Yantra X Backend Core with Journal Logging

from flask import Flask, jsonify, request
from services.notification_service import send_notification
from services.logger_service import logger
from ai_agents.macro_monk import macro_monk_decision
from ai_agents.the_ghost import ghost_signal_handler
from ai_agents.data_whisperer import analyze_data
from ai_agents.degen_auditor import audit_trade
from rl_core.rl_trainer import train_model
from rl_core.env_market_sim import MarketSimEnv
from rl_core.reward_function import calculate_reward
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# 🔹 Log trade to local SQLite journal
def log_to_journal(signal, audit, reward):
    conn = sqlite3.connect("trade_journal.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO journal_entries (timestamp, signal, audit, reward)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), signal, audit, reward))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return jsonify({"message": "🚀 Yantra X RL Backend is Live!"})

@app.route("/ping")
def ping():
    return jsonify({"status": "✅ Healthy"})

@app.route("/notify")
def test_notify():
    sent = send_notification(
        subject="🧠 Yantra X System Test",
        message="Hello from your AI trading backend.",
        to_email=os.getenv("SMTP_USER", "")
    )
    return jsonify({"notification_sent": sent})

@app.route("/run-cycle", methods=["POST"])
def run_cycle():
    market_data = analyze_data()
    logger.info(f"Market Data: {market_data}")

    strategy = macro_monk_decision(market_data)
    logger.info(f"Macro Monk Strategy: {strategy}")

    signal = ghost_signal_handler(strategy)
    logger.info(f"The Ghost Signal: {signal}")

    audit = audit_trade(signal)
    logger.info(f"Degen Auditor Result: {audit}")

    env = MarketSimEnv()
    price_change = market_data.get("price", 0) * (1 if audit == "Approved" else -1)
    reward = calculate_reward(env, price_change)
    logger.info(f"Calculated Reward: {reward}")

    train_model()

    send_notification(
        subject="Yantra X Trade Cycle",
        message=f"Signal: {signal} | Audit: {audit} | Reward: {reward}",
        to_email=os.getenv("SMTP_USER", "")
    )

    logger.info("Notification sent successfully.")

    # 🔹 Save to journal
    log_to_journal(signal, audit, reward)

    return jsonify({
        "status": "success",
        "signal": signal,
        "audit": audit,
        "reward": reward
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
