import streamlit as st
from util.database import save_meal_log, get_meal_templates, save_meal_template
from util.nutrition import get_nutrition_info
from datetime import datetime

st.title("🍱 Log a Meal")

# Select or Create a Meal Template
meal_templates = get_meal_templates()
template_names = ["-- Select Template --"] + list(meal_templates.keys())

selected_template = st.selectbox("Choose a Meal Template", template_names)

meal_items = []

if selected_template != "-- Select Template --":
    meal_items = meal_templates[selected_template]

st.subheader("Add Food Items to Meal")

with st.form("meal_form"):
    new_meal_name = st.text_input("Meal Name (e.g. Post-workout Shake, Dinner)", value=selected_template if selected_template != "-- Select Template --" else "")
    food_item = st.text_input("Food Item (e.g. Banana)")
    quantity = st.number_input("Quantity", min_value=0.0, format="%.2f")
    unit = st.selectbox("Unit", ["gm", "ml", "tbsp", "piece"])

    add_item = st.form_submit_button("Add to Meal")

    if add_item and food_item:
        meal_items.append({"food": food_item, "quantity": quantity, "unit": unit})
        st.success(f"Added {quantity} {unit} of {food_item} to the meal.")

# Show current meal items
if meal_items:
    st.subheader("Current Meal Items:")
    for i, item in enumerate(meal_items):
        st.write(f"{i+1}. {item['quantity']} {item['unit']} {item['food']}")

    # Save as template
    if st.button("💾 Save This Meal as Template"):
        if new_meal_name:
            save_meal_template(new_meal_name, meal_items)
            st.success(f"Saved template '{new_meal_name}'")
        else:
            st.warning("Please enter a name for the template.")

    # Log meal
    if st.button("✅ Log This Meal"):
        # Get nutritional info for each item
        try:
            nutrition_data = get_nutrition_info(meal_items)
            save_meal_log(new_meal_name or "Unnamed Meal", meal_items, nutrition_data, datetime.now())
            st.success("Meal logged successfully!")
        except Exception as e:
            st.error(f"Error logging meal: {e}")


