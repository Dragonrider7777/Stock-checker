import json
import os

from config.settings import PRODUCTS_FILE

def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(filename, data):
    folder = os.path.dirname(filename)

    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

def load_products():
    return load_json(PRODUCTS_FILE, [])