import json
import os
import requests

FOOD_DB_PATH = "data/food_data.json"

# util/food_utils.py

def get_valid_units_for_food(food_name):
    # You can expand this dictionary over time
    food_units = {
        "banana": ["piece"],
        "milk": ["ml", "cup"],
        "oats": ["g", "tbsp", "cup"],
        "peanut butter": ["tbsp", "g"],
        "egg": ["piece"],
        "chicken": ["g"],
        "rice": ["g", "cup"],
        "yogurt": ["g", "ml", "cup"],
        "apple": ["piece", "g"],
        "grapes": ["g", "piece"],
    }

    # Default to all common units if food is unknown
    default_units = ["g", "ml", "tbsp", "tsp", "cup", "piece"]
    return food_units.get(food_name.lower(), default_units)

def load_local_food_data():
    try:
        with open("data/food_db.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_to_food_data(name, nutrition):
    data = load_local_food_data()
    data[name.lower()] = nutrition
    with open(FOOD_DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

def fetch_nutrition_from_internet(food_name):
    # You can use OpenFoodFacts or other APIs. Here's OpenFoodFacts:
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{food_name.lower().replace(' ', '_')}.json"
        response = requests.get(url)
        data = response.json()

        if 'product' not in data or 'nutriments' not in data['product']:
            return None

        nutriments = data['product']['nutriments']
        return {
            "calories": nutriments.get("energy-kcal_100g", 0),
            "protein": nutriments.get("proteins_100g", 0),
            "carbs": nutriments.get("carbohydrates_100g", 0),
            "fats": nutriments.get("fat_100g", 0)
        }

    except Exception as e:
        return None
