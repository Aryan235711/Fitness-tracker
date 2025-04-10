# init_db.py
import sqlite3

conn = sqlite3.connect("data/user_data.db")

# Table for body metrics (already exists)
conn.execute("""
CREATE TABLE IF NOT EXISTS body_metrics (
    date TEXT,
    weight REAL,
    fat_percent REAL
);
""")

# Table for wearable data
conn.execute("""
CREATE TABLE IF NOT EXISTS wearable_data (
    date TEXT PRIMARY KEY,
    heart_rate_avg REAL,
    spo2_avg REAL,
    sleep_hours REAL,
    steps INTEGER
);
""")

# Table for simulation history
conn.execute("""
CREATE TABLE IF NOT EXISTS simulation_history (
    date TEXT,
    action TEXT,
    food TEXT,
    quantity REAL,
    unit TEXT,
    caloric_change REAL,
    duration_days INTEGER
);
""")

conn.commit()
conn.close()
print("✅ Database initialized.")
