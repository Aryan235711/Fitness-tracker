# util/db_utils.py

import sqlite3

def init_simulation_table():
    conn = sqlite3.connect("data/user_data.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        action TEXT,
        food TEXT,
        quantity REAL,
        unit TEXT,
        caloric_change REAL,
        duration_days INTEGER
    )
    """)
    conn.commit()
    conn.close()
