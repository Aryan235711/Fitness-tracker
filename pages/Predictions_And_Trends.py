import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import datetime
import json
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

# -------- Streamlit UI --------
st.title("📊 Predictions & Trends")

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

st.divider()
st.subheader("🧪 Simulate Progress by Adding/Removing Foods")

# Load food data
def load_food_data():
    with open("data/food_data.json", "r") as f:
        return json.load(f)

food_data = load_food_data()
food_names = list(food_data.keys())

st.markdown("### Simulate a dietary change")

action = st.radio("Do you want to add or remove a food item?", ["Add", "Remove"])
selected_food = st.selectbox("Choose a food item", food_names)
qty = st.number_input("Quantity (per day)", min_value=0.0, value=100.0)
unit = st.selectbox("Unit", ["g", "ml", "piece", "tbsp", "tsp", "cup"])

caloric_change = 0

if selected_food in food_data:
    cal_per_100g = food_data[selected_food].get("calories", 0)
    caloric_change = (cal_per_100g / 100) * qty
    if action == "Remove":
        caloric_change *= -1

    st.info(f"Estimated caloric change per day: **{caloric_change:.2f} kcal**")

# Show hypothetical impact on weight
st.markdown("### 📉 Hypothetical Future Prediction")

if st.button("🔍 Simulate Effect"):
    weight_df = metrics_df.dropna(subset=["weight"]).copy()
    if not weight_df.empty:
        weight_df['date'] = pd.to_datetime(weight_df['date'])
        weight_df['days_since_start'] = (weight_df['date'] - weight_df['date'].min()).dt.days
        
        X = weight_df[['days_since_start']]
        y = weight_df['weight']

        model = LinearRegression()
        model.fit(X, y)

        # Add simulated daily effect: 7700 kcal = ~1 kg
        daily_weight_change = caloric_change / 7700

        future_days = np.arange(weight_df['days_since_start'].max() + 1,
                                weight_df['days_since_start'].max() + days + 1)
        predicted_weight = model.predict(future_days.reshape(-1, 1))
        predicted_weight_sim = predicted_weight + np.cumsum([daily_weight_change] * days)

        future_dates = [weight_df['date'].max() + datetime.timedelta(days=i) for i in range(1, days + 1)]

        sim_df = pd.DataFrame({
            "date": future_dates,
            "Original Prediction": predicted_weight,
            "With Simulated Change": predicted_weight_sim
        }).set_index("date")

        st.line_chart(sim_df)
    else:
        st.warning("Not enough weight data to simulate. Please log more.")
