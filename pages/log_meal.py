import streamlit as st
import json
import os

def show_meal_logger():
    st.title("🍽️ Meal Logger")
    st.write("Log your meals and get nutritional insights here.")


TEMPLATES_FILE = "data/meal_templates.json"
UNIT_OPTIONS = ["gm", "ml", "tbsp", "tsp", "piece", "cup", "slice", "oz"]

# Create the file if it doesn't exist
if not os.path.exists(TEMPLATES_FILE):
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump({}, f)


def load_templates():
    with open(TEMPLATES_FILE, 'r') as f:
        return json.load(f)


def save_templates(templates):
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=4)


def add_meal_template():
    st.subheader("📝 Create a New Meal Template")
    meal_name = st.text_input("Meal Template Name")

    st.markdown("### Add Food Items:")
    food_items = []
    cols = st.columns([2, 1, 1])
    food = cols[0].text_input("Food", key="food1")
    qty = cols[1].number_input("Quantity", min_value=0.0, key="qty1")
    unit = cols[2].selectbox("Unit", UNIT_OPTIONS, key="unit1")

    if food:
        food_items.append({"food": food.lower(), "qty": qty, "unit": unit})

    # Allow multiple entries using session_state
    if "more_items" not in st.session_state:
        st.session_state.more_items = []

    if st.button("➕ Add Another Item"):
        st.session_state.more_items.append({"food": "", "qty": 0, "unit": "gm"})

    for i, item in enumerate(st.session_state.more_items):
        cols = st.columns([2, 1, 1])
        item["food"] = cols[0].text_input(f"Food {i+2}", key=f"food{i+2}")
        item["qty"] = cols[1].number_input(f"Qty {i+2}", min_value=0.0, key=f"qty{i+2}")
        item["unit"] = cols[2].selectbox(f"Unit {i+2}", UNIT_OPTIONS, key=f"unit{i+2}")
        food_items.append(item)

    if st.button("✅ Save Template"):
        if not meal_name:
            st.error("Please enter a name for your meal template.")
        elif any(not item["food"] for item in food_items):
            st.error("Please ensure all food names are filled.")
        else:
            templates = load_templates()
            templates[meal_name] = food_items
            save_templates(templates)
            st.success(f"'{meal_name}' template saved successfully!")
            st.session_state.more_items = []  # Reset after save


def show_saved_templates():
    st.subheader("📦 Saved Meal Templates")
    templates = load_templates()

    if not templates:
        st.info("No templates saved yet.")
        return

    for meal, items in templates.items():
        with st.expander(f"🍽 {meal}"):
            for item in items:
                st.markdown(f"- {item['food'].title()} : {item['qty']} {item['unit']}")
            col1, col2 = st.columns([1, 1])
            if col1.button(f"❌ Delete '{meal}'", key=f"del_{meal}"):
                del templates[meal]
                save_templates(templates)
                st.warning(f"Deleted '{meal}'")
                st.experimental_rerun()


def main():
    st.title("🍴 Meal Logger — Template Manager")
    st.markdown("Create, reuse, and manage your meal templates with ease.")

    tab1, tab2 = st.tabs(["➕ Add New Template", "📚 View Templates"])

    with tab1:
        add_meal_template()
    with tab2:
        show_saved_templates()


if __name__ == "__main__":
    main()
