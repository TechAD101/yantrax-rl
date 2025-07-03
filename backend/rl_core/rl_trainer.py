# rl_core/rl_trainer.py — RL Trainer & Cycle Runner

import sqlite3
import random
from datetime import datetime
from rl_core.env_market_sim import MarketSimEnv

def train_model():
    env = MarketSimEnv()
    total_reward = 0
    for ep in range(10):  # Simulate 10 episodes
        state = env.reset()
        done = False
        while not done:
            action = random.choice(env.get_action_space())
            state, reward, done = env.step(action)
            total_reward += reward

        now = datetime.now().isoformat()
        conn = sqlite3.connect("trade_journal.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rl_rewards (
                timestamp TEXT,
                episode INTEGER,
                total_reward REAL
            )
        """)
        cursor.execute(
            "INSERT INTO rl_rewards (timestamp, episode, total_reward) VALUES (?, ?, ?)",
            (now, ep + 1, round(total_reward, 2))
        )
        conn.commit()
        conn.close()
    return {"status": "trained", "total_reward": round(total_reward, 2)}

def run_rl_cycle():
    env = MarketSimEnv()
    total_reward = 0
    steps = []

    for _ in range(5):  # Simulate 5 steps
        action = random.choice(env.get_action_space())
        state, reward, done = env.step(action)
        steps.append({
            "action": action,
            "state": state,
            "reward": reward
        })
        total_reward += reward
        if done:
            break

    return {
        "final_balance": state["balance"],
        "final_mood": state["mood"],
        "final_cycle": state["cycle"],
        "curiosity": state["curiosity"],
        "total_reward": round(total_reward, 2),
        "steps": steps
    }
