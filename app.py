import streamlit as st
from pages.dashboard import show_dashboard
from pages.log_meal import show_meal_logger
from pages.log_workout import show_workout_logger
from pages.log_supplement import show_supplement_logger
from pages.progress_tracker import show_progress_tracker
from pages.ai_predictions import show_ai_predictions
from pages.body_metrics import show_body_metrics
from util.db_utils import init_simulation_table
init_simulation_table()


st.set_page_config(page_title="Fitness & Nutrition Tracker", layout="wide")

st.sidebar.title("🏋️ Navigation")
tab = st.sidebar.radio("Go to", [
    "Dashboard",
    "Log Meal",
    "Log Workout",
    "Log Supplement",
    "Progress Tracker",
    "AI Predictions",
    "Body Metrics",
])

if tab == "Dashboard":
    show_dashboard()
elif tab == "Log Meal":
    show_meal_logger()
elif tab == "Log Workout":
    show_workout_logger()
elif tab == "Log Supplement":
    show_supplement_logger()
elif tab == "Progress Tracker":
    show_progress_tracker()
elif tab == "AI Predictions":
    show_ai_predictions()
elif tab == "Body Metrics":
    show_body_metrics()
