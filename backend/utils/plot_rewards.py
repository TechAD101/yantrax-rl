# plot_rewards.py — Visualize RL reward progression

import sqlite3
import matplotlib.pyplot as plt
import os

def plot_rewards():
    # ✅ Absolute path to shared DB
    db_path = os.path.join(os.path.dirname(__file__), "..", "trade_journal.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("SELECT episode, reward FROM rl_rewards ORDER BY episode ASC")
    data = cursor.fetchall()
    conn.close()

    episodes = [row[0] for row in data]
    rewards = [row[1] for row in data]

    plt.figure(figsize=(10, 5))
    plt.plot(episodes, rewards, marker='o', linestyle='-', color='gold')
    plt.title("📈 Yantra X – RL Reward Curve")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("rl_rewards_plot.png")
    plt.show()

if __name__ == "__main__":
    plot_rewards()
