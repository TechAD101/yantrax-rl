# init_journal.py — Initialize RL and journal tables

import sqlite3

conn = sqlite3.connect("trade_journal.db")
cursor = conn.cursor()


# Journal entries (daily logs) with index
cursor.execute("""
CREATE TABLE IF NOT EXISTS journal_entries (
    timestamp TEXT,
    signal TEXT,
    audit TEXT,
    reward REAL
)
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_journal_timestamp ON journal_entries(timestamp);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_journal_signal ON journal_entries(signal);")

# RL training logs (episode-based rewards) with index
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
cursor.execute("CREATE INDEX IF NOT EXISTS idx_rl_episode ON rl_rewards(episode);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_rl_timestamp ON rl_rewards(timestamp);")

conn.commit()
conn.close()

print("✅ All tables created successfully.")
