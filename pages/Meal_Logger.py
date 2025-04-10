import streamlit as st
import json
import os

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

    meal_names = list(templates.keys())
    selected_meal_to_edit = st.selectbox("✏️ Select a meal to edit", [""] + meal_names)

    if selected_meal_to_edit:
        st.markdown("### 🛠 Edit Ingredients")
        original_ingredients = templates[selected_meal_to_edit].copy()
        edited_ingredients = original_ingredients.copy()

        # Show current ingredients
        for i, item in enumerate(original_ingredients):
            st.markdown(f"- {item['food'].title()} : {item['qty']} {item['unit']}")

        # Remove ingredient
        food_options = [item['food'] for item in edited_ingredients]
        ingredient_to_remove = st.selectbox("🔻 Select ingredient to remove", ["None"] + food_options)
        if ingredient_to_remove != "None":
            if st.button("Remove Selected Ingredient"):
                edited_ingredients = [item for item in edited_ingredients if item['food'] != ingredient_to_remove]
                st.success(f"✅ Removed '{ingredient_to_remove}'")

        # Add or update ingredient
        st.markdown("### ➕ Add/Update Ingredient")
        new_food = st.text_input("Food name")
        new_qty = st.text_input("Quantity (e.g., 100)")
        if new_food:
            valid_units = get_valid_units_for_food(new_food)
        else:
            valid_units = ["g", "ml", "tbsp", "tsp", "cup", "piece"]
        
        new_unit = st.selectbox("Unit", valid_units)

        if new_food and new_qty:
            try:
                new_qty_float = float(new_qty)
                # Check if it already exists
                found = False
                for item in edited_ingredients:
                    if item['food'] == new_food:
                        item['qty'] = new_qty_float
                        item['unit'] = new_unit
                        found = True
                        break
                if not found:
                    edited_ingredients.append({
                        "food": new_food,
                        "qty": new_qty_float,
                        "unit": new_unit
                    })
                st.success(f"✅ Added/Updated '{new_food}'")
            except ValueError:
                st.error("Please enter a valid number for quantity.")

        # Save button
        if st.button("💾 Save Changes"):
            templates[selected_meal_to_edit] = edited_ingredients
            save_templates(templates)
            st.success(f"✅ Saved changes to '{selected_meal_to_edit}'")

        # Undo button
        if st.button("↩️ Undo Changes"):
            templates = load_templates()
            st.warning("Changes reverted. Reloaded last saved version.")

        # Delete template
        if st.button(f"❌ Delete '{selected_meal_to_edit}'"):
            del templates[selected_meal_to_edit]
            save_templates(templates)
            st.warning(f"🗑 Deleted '{selected_meal_to_edit}'")
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
