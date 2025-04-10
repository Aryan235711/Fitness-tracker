# pages/ai_predictions.py

import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import datetime
import matplotlib.pyplot as plt
import xgboost as xgb
from util.food_utils import load_local_food_data
import plotly.graph_objects as go
import plotly.express as px
from ml.xgboost_model import load_training_data, train_xgb_models, predict_future as predict_xgb


DB_PATH = "data/user_data.db"

# ---------- DB & Prediction Helpers ----------
def load_metrics():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT date, weight, fat_percent FROM body_metrics ORDER BY date", conn)
    conn.close()
    return df

def predict_future(df, calorie_offset=0, target_days=30):
    if df.empty or df.shape[0] < 2:
        return None

    # Step 1: Load wearable data
    conn = sqlite3.connect(DB_PATH)
    wearable_df = pd.read_sql_query("SELECT * FROM wearable_data", conn)
    conn.close()

    if wearable_df.empty:
        wearable_df = pd.DataFrame(columns=["date", "heart_rate_avg", "spo2_avg", "sleep_hours", "steps"])

    wearable_df['date'] = pd.to_datetime(wearable_df['date'])
    df['date'] = pd.to_datetime(df['date'])

    # Step 2: Merge
    merged_df = pd.merge(df, wearable_df, on='date', how='left')

    # Fill missing wearable data with mean or 0 (if no wearable data at all)
    merged_df.fillna(method='ffill', inplace=True)
    merged_df.fillna(method='bfill', inplace=True)
    merged_df.fillna(0, inplace=True)

    merged_df['days_since_start'] = (merged_df['date'] - merged_df['date'].min()).dt.days

    preds = {}
    features = ['days_since_start', 'sleep_hours', 'steps', 'heart_rate_avg', 'spo2_avg']

    for col in ['weight', 'fat_percent']:
        if merged_df[col].isnull().any():
            continue

        X = merged_df[features]
        y = merged_df[col]

        model = xgb.XGBRegressor(n_estimators=100, objective='reg:squarederror')
        model.fit(X, y)

        # Create future data
        last_day = merged_df['days_since_start'].max()
        future_days = np.arange(last_day + 1, last_day + target_days + 1)

        future_df = pd.DataFrame({
            'days_since_start': future_days,
            'sleep_hours': merged_df['sleep_hours'].mean(),
            'steps': merged_df['steps'].mean(),
            'heart_rate_avg': merged_df['heart_rate_avg'].mean(),
            'spo2_avg': merged_df['spo2_avg'].mean()
        })

        future_pred = model.predict(future_df)

        # Apply calorie offset for weight
        if col == 'weight':
            weight_offset = calorie_offset / 7700
            future_pred += weight_offset

        future_dates = [merged_df['date'].max() + datetime.timedelta(days=i) for i in range(1, target_days + 1)]
        preds[col] = pd.DataFrame({'date': future_dates, col: future_pred})

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

# ---------- Streamlit UI ----------
st.title("📊 Predictions & Simulations")

metrics_df = load_metrics()
if metrics_df.empty:
    st.warning("No body metrics data found. Please log weight and fat% in the 'Body Metrics' tab first.")
    st.stop()

st.subheader("📈 Historical Trends")
st.plotly_chart(px.line(metrics_df, x='date', y=['weight', 'fat_percent'], 
                        labels={'value': 'Metric Value', 'variable': 'Metric'},
                        title='📈 Historical Trends (Weight & Fat%)'))

# ---------- Future Predictions ----------
st.subheader("🔮 Future Predictions")
days = st.slider("Predict for how many days ahead?", 7, 90, 30)
predictions = predict_future(metrics_df, target_days=days)

if predictions:
    for key, pred_df in predictions.items():
        fig = px.line(pred_df, x='date', y=key, title=f'🔮 Predicted {key.replace("_", " ").title()}')
        st.plotly_chart(fig)
else:
    st.info("Not enough data to predict. Please log more metrics over time.")

# ---------- Simulation: Custom Calorie Input ----------
st.subheader("🧪 Simulate Adding or Removing a Food (Manual Entry)")
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

# wearables log data
st.subheader("📲 Log Wearable Data (Manual)")

with st.form("wearable_form"):
    date = st.date_input("Date", datetime.date.today())
    heart_rate = st.number_input("Average Heart Rate (bpm)", min_value=30.0, max_value=200.0)
    spo2 = st.number_input("Average SpO₂ (%)", min_value=70.0, max_value=100.0)
    sleep = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0)
    steps = st.number_input("Steps", min_value=0)
    submit = st.form_submit_button("Save")

    if submit:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT OR REPLACE INTO wearable_data (date, heart_rate_avg, spo2_avg, sleep_hours, steps)
            VALUES (?, ?, ?, ?, ?)
        """, (str(date), heart_rate, spo2, sleep, steps))
        conn.commit()
        conn.close()
        st.success("Wearable data saved successfully!")
        
# ---------- Simulation History ----------
st.divider()
st.subheader("📜 Simulation History")
history = fetch_simulation_history()
if history.empty:
    st.info("No simulation history yet.")
else:
    st.dataframe(history)

# ---------- Food Database-Based Simulation ----------
st.subheader("🍽 Simulate Impact of Food Changes from Food DB")

food_data = load_local_food_data()
if not food_data:
    st.info("No food data available. Please log meals to build food DB.")
    st.stop()

food_names = list(food_data.keys())
selected_food = st.selectbox("Choose a food item", food_names)

qty2 = st.number_input("Quantity to simulate (e.g., 100g/ml)", value=100, key="sim_qty")
unit2 = st.text_input("Unit (just for reference)", value="g", key="sim_unit")
action2 = st.radio("Action", ["➕ Add daily", "➖ Remove daily"], key="sim_action")

# Calculate kcal impact
kcal_per_100 = food_data[selected_food]["calories"]
total_kcal = kcal_per_100 * (qty2 / 100)
if "Remove" in action2:
    total_kcal = -total_kcal

# Simulate weight change
weight_change_per_day = total_kcal / 7700.0
sim_days = 30
today = pd.Timestamp.today()
sim_dates = [today + pd.Timedelta(days=i) for i in range(sim_days)]
start_weight = metrics_df['weight'].iloc[-1]
sim_weights = [start_weight + i * weight_change_per_day for i in range(sim_days)]

sim_df = pd.DataFrame({
    "date": sim_dates,
    "simulated_weight": sim_weights
})

st.markdown(f"🔍 Simulating **{action2.lower()}** `{selected_food}` ({qty2}{unit2}) for next {sim_days} days.")

fig = px.line(sim_df, x="date", y="simulated_weight", 
              title="📈 Simulated Weight Over Time",
              labels={"simulated_weight": "Weight (kg)"})
st.plotly_chart(fig)

# Download Simulation Data
st.subheader("⬇️ Export Simulation Data")

csv = sim_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download as CSV",
    data=csv,
    file_name=f'{selected_food.lower().replace(" ", "_")}_simulation.csv',
    mime='text/csv'
)

# Show Wearable History (Diagnostics)
st.divider()
st.subheader("📋 Logged Wearable Data")

conn = sqlite3.connect(DB_PATH)
wearable_data_df = pd.read_sql_query("SELECT * FROM wearable_data ORDER BY date DESC", conn)
conn.close()

if wearable_data_df.empty:
    st.info("No wearable data logged yet.")
else:
    st.dataframe(wearable_data_df)



