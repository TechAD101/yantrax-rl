# init_journal.py — Initialize RL and journal tables

import sqlite3

conn = sqlite3.connect("trade_journal.db")
cursor = conn.cursor()

# Journal entries (daily logs)
cursor.execute("""
CREATE TABLE IF NOT EXISTS journal_entries (
    timestamp TEXT,
    signal TEXT,
    audit TEXT,
    reward REAL
)
""")

# RL training logs (episode-based rewards)
cursor.execute("""
CREATE TABLE IF NOT EXISTS rl_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    episode INTEGER,
    strategy TEXT,
    emotion TEXT,
    audit TEXT,
    reward REAL
)
""")

conn.commit()
conn.close()

print("✅ All tables created successfully.")
