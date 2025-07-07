# backend/create_agent_commentary_table.py

import sqlite3

conn = sqlite3.connect("trade_journal.db")
cursor = conn.cursor()

# Recreate journal_entries table
cursor.execute("""
CREATE TABLE IF NOT EXISTS journal_entries (
    timestamp TEXT,
    signal TEXT,
    audit TEXT,
    reward REAL
);
""")

# Recreate agent_commentary table
cursor.execute("""
CREATE TABLE IF NOT EXISTS agent_commentary (
    timestamp TEXT,
    agent TEXT,
    comment TEXT
);
""")

conn.commit()
conn.close()

print("✅ Fresh database with journal_entries and agent_commentary tables created.")
