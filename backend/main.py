# main.py — Final Unified Yantra X Backend (RL + Agents + Frontend Ready)

from flask import Flask, jsonify, request
from services.notification_service import send_notification
from services.logger_service import logger
from ai_agents.macro_monk import macro_monk_decision
from ai_agents.the_ghost import ghost_signal_handler
from ai_agents.data_whisperer import analyze_data
from ai_agents.degen_auditor import audit_trade
from rl_core.rl_trainer import train_model, run_rl_cycle
from rl_core.env_market_sim import MarketSimEnv
from rl_core.reward_function import calculate_reward
import sqlite3
import os
from datetime import datetime
import logging
import sys

app = Flask(__name__)

# 🛠 Patch Windows logging issue (emoji-safe)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, encoding='utf-8')


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
    return jsonify({"message": "Yantra X RL Backend is Live"})


@app.route("/ping")
def ping():
    return jsonify({"status": "healthy"})


@app.route("/notify")
def test_notify():
    sent = send_notification(
        subject="Yantra X System Test",
        message="Hello from your AI trading backend.",
        to_email=os.getenv("SMTP_USER", "")
    )
    return jsonify({"notification_sent": sent})


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


@app.route("/train", methods=["POST"])
def trigger_training():
    result = train_model()
    return jsonify(result)


@app.route("/god-cycle", methods=["GET"])
def run_god_cycle():
    try:
        result = run_rl_cycle()
        return jsonify(result)
    except Exception as e:
        logger.error(f"RL Cycle error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/journal", methods=["GET"])
def view_journal():
    conn = sqlite3.connect("trade_journal.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM journal_entries ORDER BY timestamp DESC LIMIT 100")
    entries = cursor.fetchall()
    conn.close()

    journal_list = [dict(
        timestamp=row[0],
        signal=row[1],
        audit=row[2],
        reward=row[3]
    ) for row in entries]

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
