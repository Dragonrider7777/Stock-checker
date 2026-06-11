from datetime import datetime

from stores import bestbuy, pokemon_center, generic
from alerts.alert_manager import send_alert
from utils.json_utils import load_json, save_json
from utils.history_utils import add_to_history
from config.settings import STATE_FILE, DASHBOARD_FILE, HISTORY_FILE

STORE_CHECKERS = {
    "bestbuy": bestbuy.check,
    "pokemon_center": pokemon_center.check,
    "generic": generic.check
}

def process_product(page, product):
    print(f"\nChecking {product['name']}...")

    state = load_json(STATE_FILE, {})
    dashboard = load_json(DASHBOARD_FILE, [])

    store = product.get("store", "generic")
    checker = STORE_CHECKERS.get(store, generic.check)

    try:
        raw_result = checker(page, product)

        result = {
            "name": product["name"],
            "store": product["store"],
            "url": product["url"],
            "price": raw_result["price"],
            "max_price": product["max_price"],
            "in_stock": raw_result["in_stock"],
            "marketplace": raw_result["marketplace"],
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        result["good_price"] = (
            result["price"] is not None
            and result["price"] <= result["max_price"]
        )

        old_result = state.get(product["name"])

        print(f"Price: {result['price']}")
        print(f"In stock: {result['in_stock']}")
        print(f"Good price: {result['good_price']}")
        print(f"Marketplace: {result['marketplace']}")

        # Save history
        add_to_history(HISTORY_FILE, result)

        # Send alerts
        if should_alert(old_result, result):
            send_alert(product, result)
        else:
            print("No alert needed.")
        
        state[product["name"]] = result

        dashboard = [
            item for item in dashboard
            if item["name"] != product["name"]
        ]
        dashboard.append(result)

        save_json(STATE_FILE, state)
        save_json(DASHBOARD_FILE, dashboard)

    except Exception as e:
        print(f"Error checking{product['name']}: {e}")
        

def should_alert(old_result, new_result):
    if new_result["marketplace"]:
        return False
    
    if not new_result["in_stock"]:
        return False
    
    if not new_result["good_price"]:
        return False
    
    if old_result is None:
        return True
    
    became_in_stock = not old_result.get("in_stock") and new_result["in_stock"]
    became_good_price = not old_result.get("good_price") and new_result["good_price"]

    old_price = old_result.get("price")
    new_price = new_result.get("price")

    price_dropped = (
        old_price is not None
        and new_price is not None
        and new_price < old_price
    )

    return became_in_stock or became_good_price or price_dropped


