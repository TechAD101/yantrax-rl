import sqlite3

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

conn.commit()
conn.close()

print("✅ Journal table created successfully.")
