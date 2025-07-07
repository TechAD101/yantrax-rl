import sqlite3
from datetime import datetime

conn = sqlite3.connect("trade_journal.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO agent_commentary (timestamp, agent, comment)
VALUES (?, ?, ?)
""", (
    datetime.now().isoformat(),
    "Macro Monk",
    "Watching inflation closely. Might reduce exposure if CPI spikes again."
))

conn.commit()
conn.close()
print("✅ Test commentary inserted.")
