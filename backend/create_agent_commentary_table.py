# backend/create_agent_commentary_table.py

import sqlite3

conn = sqlite3.connect("trade_journal.db")
cursor = conn.cursor()


# Recreate journal_entries table with index
cursor.execute("""
CREATE TABLE IF NOT EXISTS journal_entries (
    timestamp TEXT,
    signal TEXT,
    audit TEXT,
    reward REAL
);
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_journal_timestamp ON journal_entries(timestamp);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_journal_signal ON journal_entries(signal);")

# Recreate agent_commentary table with index
cursor.execute("""
CREATE TABLE IF NOT EXISTS agent_commentary (
    timestamp TEXT,
    agent TEXT,
    comment TEXT
);
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_commentary_agent ON agent_commentary(agent);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_commentary_timestamp ON agent_commentary(timestamp);")

conn.commit()
conn.close()

print("✅ Fresh database with journal_entries and agent_commentary tables created.")
