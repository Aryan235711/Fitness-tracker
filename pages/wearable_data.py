import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

DB_PATH = "data/user_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wearable_data (
            date TEXT PRIMARY KEY,
            heart_rate_avg REAL,
            spo2_avg REAL,
            sleep_hours REAL,
            steps INTEGER
        );
    """)
    conn.commit()
    conn.close()

def insert_wearable_data(df):
    conn = sqlite3.connect(DB_PATH)
    for _, row in df.iterrows():
        conn.execute("""
            INSERT OR REPLACE INTO wearable_data (date, heart_rate_avg, spo2_avg, sleep_hours, steps)
            VALUES (?, ?, ?, ?, ?)
        """, (row['date'], row['heart_rate_avg'], row['spo2_avg'], row['sleep_hours'], row['steps']))
    conn.commit()
    conn.close()

def load_wearable_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM wearable_data ORDER BY date", conn)
    conn.close()
    return df

# ---------- Streamlit UI ----------
st.title("⌚ Wearable Data Tracker")

init_db()

st.subheader("📤 Upload Wearable CSV")
with st.expander("CSV Format Guide"):
    st.markdown("""
    Your CSV file should have the following headers:

    - `date` (YYYY-MM-DD)
    - `heart_rate_avg`
    - `spo2_avg`
    - `sleep_hours`
    - `steps`
    """)

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    try:
        df['date'] = pd.to_datetime(df['date']).dt.date.astype(str)
        insert_wearable_data(df)
        st.success("Wearable data uploaded successfully!")
    except Exception as e:
        st.error(f"Error processing file: {e}")

# ---------- Display and Visualize ----------
wearable_df = load_wearable_data()
if wearable_df.empty:
    st.info("No data available.")
else:
    st.subheader("📊 Trends from Wearables")
    for metric in ['heart_rate_avg', 'spo2_avg', 'sleep_hours', 'steps']:
        st.plotly_chart(px.line(wearable_df, x='date', y=metric, title=f"{metric.replace('_', ' ').title()}"))

