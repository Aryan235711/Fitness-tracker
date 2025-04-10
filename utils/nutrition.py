# External API integration placeholder
import random

# Placeholder function — will be replaced later with actual API + validation
def get_nutrition_info(items):
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0

    for item in items:
        name = item["food"].lower()
        qty = item["quantity"]

        if name not in food_data:
            fetched = fetch_nutrition_from_internet(name)
            if fetched is None:
                raise ValueError(f"'{name}' is not a valid food item or not found online.")
            save_to_food_data(name, fetched)
            food_data[name] = fetched

        food_info = food_data[name]
        total_calories += (food_info["calories"] / 100) * qty
        total_protein += (food_info["protein"] / 100) * qty
        total_carbs += (food_info["carbs"] / 100) * qty
        total_fats += (food_info["fats"] / 100) * qty

    return {
        "calories": round(total_calories, 2),
        "protein": round(total_protein, 2),
        "carbs": round(total_carbs, 2),
        "fats": round(total_fats, 2)
    }

