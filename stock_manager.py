from datetime import datetime

from alerts.alert_manager import send_alert
from config.settings import STATE_FILE, DASHBOARD_FILE, HISTORY_FILE
from stores import bestbuy, generic, pokemon_center, walmart
from utils.history_utils import add_to_history
from utils.json_utils import load_json, save_json

STORE_CHECKERS = {
    "bestbuy": bestbuy.check,
    "pokemon_center": pokemon_center.check,
    "walmart": walmart.check,
    "generic": generic.check,
}


def process_product(page, product):
    print(f"\nChecking {product['name']}...", flush=True)

    state = load_json(STATE_FILE, {})
    dashboard = load_json(DASHBOARD_FILE, [])

    store = product.get("store", "generic")
    checker = STORE_CHECKERS.get(store, generic.check)

    try:
        raw_result = checker(page, product)

        price = raw_result.get("price")
        max_price = product["max_price"]

        result = {
            "name": product["name"],
            "store": product["store"],
            "sku": product.get("sku"),
            "url": raw_result.get("product_url", product.get("url")),
            "price": price,
            "price_reason": raw_result.get("price_reason"),
            "max_price": max_price,
            "in_stock": raw_result.get("in_stock", False),
            "stcok_reason": raw_result.get("stock_reason"),
            "marketplace": raw_result.get("marketplace", True),
            "seller": raw_result.get("seller"),
            "seller_reason": raw_result.get("seller_reason"),
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        result["good_price"] = price is not None and price <= max_price
        result["ignored_reason"] = get_ignored_reason(result)

        old_result = state.get(product["name"])

        print(f"Price: {result['price']}")
        print(f"Price reason: {result['price_reason']}")
        print(f"In stock: {result['in_stock']}")
        print(f"Good price: {result['good_price']}")
        print(f"Marketplace: {result['marketplace']}")
        print(f"Seller: {result['seller']}")
        print(f"Seller reason: {result['seller_reason']}")
        print(f"Ignored reason: {result['ignored_reason']}")

        # Save history
        add_to_history(HISTORY_FILE, result)

        # Send alerts
        if should_alert(old_result, result):
            send_alert(product, result)
        else:
            print("No alert needed.")

        state[product["name"]] = result

        dashboard = [item for item in dashboard if item["name"] != product["name"]]
        dashboard.append(result)

        save_json(STATE_FILE, state)
        save_json(DASHBOARD_FILE, dashboard)

    except Exception as e:
        print(f"Error checking {product['name']}: {e}")


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
        old_price is not None and new_price is not None and new_price < old_price
    )

    return became_in_stock or became_good_price or price_dropped


def get_ignored_reason(result):
    if result["marketplace"]:
        return result.get("seller_reason") or "Marketplace or untrusted seller"

    if not result["in_stock"]:
        return "Product is not in stock"

    if result["price"] is None:
        return "Price could not be found"

    if not result["good_price"]:
        return "Price is above max price"

    return None
