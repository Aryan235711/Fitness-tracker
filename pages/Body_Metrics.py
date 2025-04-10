import streamlit as st
import sqlite3
import datetime

DB_PATH = "data/user_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS body_metrics (
            date TEXT PRIMARY KEY,
            weight REAL,
            height_cm REAL,
            bmi REAL,
            fat_percent REAL,
            waist_cm REAL,
            biceps_cm REAL,
            lats_cm REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_metrics(data):
    conn = sqlite3.connect(DB_PATH)
    placeholders = ','.join(['?'] * len(data))
    conn.execute(f'''
        INSERT OR REPLACE INTO body_metrics 
        (date, weight, height_cm, bmi, fat_percent, waist_cm, biceps_cm, lats_cm)
        VALUES ({placeholders})
    ''', tuple(data.values()))
    conn.commit()
    conn.close()

def calculate_bmi(weight, height_cm):
    if weight and height_cm:
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 2)
    return None

# ---------------- Streamlit UI ----------------
init_db()

st.title("📏 Body Metrics Logger")

today = datetime.date.today()
st.write("Log your body metrics for:", today)

weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, step=0.1)
height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, step=0.1)
bmi = calculate_bmi(weight, height_cm)

st.markdown(f"**Calculated BMI:** {bmi if bmi else '—'}")

fat_percent = st.number_input("Fat %", min_value=0.0, max_value=100.0, step=0.1)
waist = st.number_input("Waist (cm)", min_value=20.0, max_value=200.0, step=0.1)
biceps = st.number_input("Biceps (cm)", min_value=10.0, max_value=80.0, step=0.1)
lats = st.number_input("Lats (cm)", min_value=20.0, max_value=200.0, step=0.1)

if st.button("✅ Save Metrics"):
    data = {
        "date": str(today),
        "weight": weight,
        "height_cm": height_cm,
        "bmi": bmi,
        "fat_percent": fat_percent,
        "waist_cm": waist,
        "biceps_cm": biceps,
        "lats_cm": lats
    }
    save_metrics(data)
    st.success("Metrics saved successfully!")
