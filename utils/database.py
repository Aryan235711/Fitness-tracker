# SQLite DB operations placeholder
import json
import os
from datetime import datetime

DB_PATH = "data/meal_logs.json"
TEMPLATE_PATH = "data/meal_templates.json"

def save_meal_log(name, items, nutrition, timestamp):
    os.makedirs("data", exist_ok=True)
    log = {
        "name": name,
        "items": items,
        "nutrition": nutrition,
        "timestamp": timestamp.isoformat()
    }
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log)
    with open(DB_PATH, "w") as f:
        json.dump(logs, f, indent=4)

def get_meal_templates():
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_meal_template(name, items):
    templates = get_meal_templates()
    templates[name] = items
    with open(TEMPLATE_PATH, "w") as f:
        json.dump(templates, f, indent=4)

