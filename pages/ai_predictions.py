# File: pages/ai_predictions.py

import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import datetime
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from util.food_utils import load_local_food_data

DB_PATH = "data/user_data.db"

def load_metrics():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT date, weight, fat_percent FROM body_metrics ORDER BY date", conn)
    conn.close()
    return df

def predict_future(df, calorie_offset=0, target_days=30):
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

        # Apply calorie offset (assuming ~7700 kcal = 1kg change)
        if col == 'weight':
            weight_offset = calorie_offset / 7700
            predictions += weight_offset

        future_dates = [df['date'].max() + datetime.timedelta(days=i) for i in range(1, target_days + 1)]
        preds[col] = pd.DataFrame({'date': future_dates, col: predictions})

    return preds

def log_simulation(action, food, qty, unit, kcal_change, duration):
    conn = sqlite3.connect(DB_PATH)
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

# ---------------- UI Starts ----------------
st.title("📊 Predictions & Simulations")

metrics_df = load_metrics()

if metrics_df.empty:
    st.warning("No body metrics data found. Please log weight and fat% in the 'Body Metrics' tab first.")
    st.stop()

st.subheader("📈 Historical Trends")
st.line_chart(metrics_df.set_index("date")[['weight', 'fat_percent']])

st.subheader("🔮 Future Predictions")
days = st.slider("Predict for how many days ahead?", 7, 90, 30)
predictions = predict_future(metrics_df, target_days=days)

if predictions:
    for key, df in predictions.items():
        st.markdown(f"**Predicted {key.replace('_', ' ').title()}**")
        st.line_chart(df.set_index("date"))
else:
    st.info("Not enough data to predict.")

# ---------------- Simulation ----------------
st.divider()
st.subheader("🧪 Simulate Add/Remove Foods")

food_db = load_local_food_data()
food_names = list(food_db.keys())
action = st.radio("Choose an action:", ["Add Food", "Remove Food"], horizontal=True)

selected_foods = st.multiselect("Select food(s) to simulate:", food_names)
qty_dict = {}
for food in selected_foods:
    qty_dict[food] = st.number_input(f"{food.title()} quantity (in g/ml/piece):", min_value=1, value=100, step=10)

simulate = st.button("Run Simulation")

if simulate and selected_foods:
    total_kcal = 0
    for food in selected_foods:
        cal_per_100g = food_db[food]["calories"]
        amount = qty_dict[food]
        effect = 1 if action == "Add Food" else -1
        change = effect * (cal_per_100g * amount / 100)
        total_kcal += change
        log_simulation(action, food, amount, "unit", change, days)

    st.markdown(f"**Estimated total calorie {'surplus' if total_kcal > 0 else 'deficit'}: {abs(total_kcal):.2f} kcal**")
    
    simulated_preds = predict_future(metrics_df, calorie_offset=total_kcal, target_days=days)

    st.markdown("### 🆚 Original vs Simulated Predictions")

    for key in ['weight', 'fat_percent']:
        if key in predictions and key in simulated_preds:
            df1 = predictions[key].set_index("date").rename(columns={key: "Original"})
            df2 = simulated_preds[key].set_index("date").rename(columns={key: "Simulated"})
            st.line_chart(pd.concat([df1, df2], axis=1))

# ---------------- History ----------------
st.divider()
st.subheader("📜 Simulation History")

history = fetch_simulation_history()
if not history.empty:
    st.dataframe(history)
else:
    st.info("No simulation history yet.")
