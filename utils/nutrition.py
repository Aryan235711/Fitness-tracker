# External API integration placeholder
import random

# Placeholder function — will be replaced later with actual API + validation
def get_nutrition_info(items):
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0

    for item in items:
        qty = item["quantity"]
        # Dummy values
        total_calories += qty * random.uniform(0.5, 2)
        total_protein += qty * random.uniform(0.05, 0.2)
        total_carbs += qty * random.uniform(0.1, 0.3)
        total_fats += qty * random.uniform(0.02, 0.1)

    return {
        "calories": round(total_calories, 2),
        "protein": round(total_protein, 2),
        "carbs": round(total_carbs, 2),
        "fats": round(total_fats, 2)
    }

