# pages/ai_predictions.py
import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import datetime
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

DB_PATH = "data/user_data.db"

def load_metrics():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT date, weight, fat_percent FROM body_metrics ORDER BY date", conn)
    conn.close()
    return df

def predict_future(df, target_days=30):
    if df.empty or df.shape[0] < 2:
        return None

    df['date'] = pd.to_datetime(df['date'])
    df['days_since_start'] = (df['date'] - df['date'].min()).dt.days

    X = df[['days_since_start']]
    preds = {}

    for col in ['weight', 'fat_percent']:
        if df[col].isnull().any():
            continue
        y = df[col]
        model = LinearRegression()
        model.fit(X, y)

        future_days = np.arange(df['days_since_start'].max() + 1,
                                df['days_since_start'].max() + target_days + 1).reshape(-1, 1)
        predictions = model.predict(future_days)

        future_dates = [df['date'].max() + datetime.timedelta(days=i) for i in range(1, target_days + 1)]
        preds[col] = pd.DataFrame({'date': future_dates, col: predictions})

    return preds

def log_simulation(action, food, qty, unit, kcal_change, duration):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO simulation_history (date, action, food, quantity, unit, caloric_change, duration_days)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        action, food, qty, unit, kcal_change, duration
    ))
    conn.commit()
    conn.close()

def fetch_simulation_history():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM simulation_history ORDER BY date DESC", conn)
    conn.close()
    return df


# -------- Streamlit UI --------
st.title("📊 Predictions & Simulations")

metrics_df = load_metrics()

if metrics_df.empty:
    st.warning("No body metrics data found. Please log weight and fat% in the 'Body Metrics' tab first.")
    st.stop()

st.subheader("📈 Historical Trends")
st.line_chart(metrics_df.set_index("date")[['weight', 'fat_percent']])

st.subheader("🔮 Future Predictions")
days = st.slider("Predict for how many days ahead?", 7, 90, 30)

predictions = predict_future(metrics_df, days)

if predictions:
    for key, df in predictions.items():
        st.markdown(f"**Predicted {key.replace('_', ' ').title()}**")
        st.line_chart(df.set_index("date"))
else:
    st.info("Not enough data to predict. Please log more metrics over time.")

# 🔁 Simulation Section
st.subheader("🧪 Simulate Adding or Removing a Food")
with st.form("simulate_form"):
    action = st.radio("Simulation Type", ["Add Food", "Remove Food"])
    food = st.text_input("Food Name", placeholder="e.g. Banana")
    qty = st.number_input("Quantity", min_value=0.0, step=0.1)
    unit = st.selectbox("Unit", ["g", "ml", "tbsp", "piece", "cup"])
    kcal_per_100g = st.number_input("Estimated Calories per 100g/ml", min_value=0.0, step=1.0)
    duration = st.slider("Simulate over (days)", 7, 90, 30)
    submitted = st.form_submit_button("Run Simulation")

    if submitted and food and kcal_per_100g > 0:
        actual_kcal = (qty / 100) * kcal_per_100g
        if action == "Remove Food":
            actual_kcal = -actual_kcal
        log_simulation(action, food, qty, unit, actual_kcal, duration)
        st.success(f"Logged simulation of {action.lower()} {qty}{unit} {food} with {actual_kcal:.2f} kcal change.")
        st.experimental_rerun()

# 🧾 Show simulation history
st.divider()
st.subheader("📜 Simulation History")

history = fetch_simulation_history()
if history.empty:
    st.info("No simulation history yet.")
else:
    st.dataframe(history)

def show_ai_predictions():
    st.title("🤖 AI Predictions")
    st.write("Get predictive insights based on your data.")
