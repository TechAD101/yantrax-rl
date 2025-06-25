# main.py - Placeholder content for RL-enhanced Yantra X
from flask import Flask
from services.notification_service import send_notification
from ai_agents.macro_monk import macro_monk_decision
from ai_agents.the_ghost import ghost_signal_handler
from ai_agents.data_whisperer import analyze_data
from ai_agents.degen_auditor import audit_trade
from rl_core.rl_trainer import train_model
from rl_core.env_market_sim import MarketSimEnv
from rl_core.reward_function import calculate_reward

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to Yantra X Backend 🚀"

@app.route("/run-cycle", methods=["POST"])
def run_cycle():
    market_data = analyze_data()
    strategy = macro_monk_decision(market_data)
    signal = ghost_signal_handler(strategy)
    audit = audit_trade(signal)

    env = MarketSimEnv()
    reward = calculate_reward(env)
    train_model()

    send_notification(f"Trade Decision: {signal} | Audit: {audit} | Reward: {reward}")
    return {"status": "success", "signal": signal, "reward": reward}

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, jsonify
from services.notification_service import send_notification
import os

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
