# ml/xgboost_model.py
import sqlite3
import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import datetime

DB_PATH = "data/user_data.db"

def load_training_data():
    conn = sqlite3.connect(DB_PATH)

    metrics = pd.read_sql_query("""
        SELECT date, weight, fat_percent
        FROM body_metrics
        ORDER BY date
    """, conn)

    meals = pd.read_sql_query("""
        SELECT date, SUM(calories) as total_calories
        FROM meals
        GROUP BY date
    """, conn)

    conn.close()

    # Preprocess
    metrics['date'] = pd.to_datetime(metrics['date'])
    meals['date'] = pd.to_datetime(meals['date'])

    df = pd.merge(metrics, meals, on='date', how='left')
    df['total_calories'].fillna(0, inplace=True)
    df['day'] = (df['date'] - df['date'].min()).dt.days

    return df

def train_xgb_models(df):
    models = {}

    for target in ['weight', 'fat_percent']:
        if df[target].isnull().any():
            continue

        X = df[['day', 'total_calories']]
        y = df[target]

        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
        model.fit(X, y)
        models[target] = model

    return models

def predict_future(models, df, future_days=30, calorie_override=None):
    last_day = df['day'].max()
    last_cal = df['total_calories'].iloc[-1] if calorie_override is None else calorie_override

    future = pd.DataFrame({
        'day': range(last_day + 1, last_day + future_days + 1),
        'total_calories': [last_cal] * future_days
    })

    preds = {}
    for key, model in models.items():
        preds[key] = model.predict(future)

    future['date'] = pd.date_range(start=df['date'].max() + pd.Timedelta(days=1), periods=future_days)
    for key in preds:
        future[key] = preds[key]

    return future

