from dotenv import load_dotenv

load_dotenv()

import json
from providers.walmart import check_walmart
from alerts.alert_manager import send_alert

# from providers.bestbuy import check_bestbuy

PROVIDERS = {
    "walmart": check_walmart,
    # "bestbuy": check_bestbuy,
}


def seller_allowed(result, store_config):
    seller = (result.get("seller") or "").lower()

    allowed = [s.lower() for s in store_config.get("allowed_sellers", [])]
    blocked = [s.lower() for s in store_config.get("blocked_sellers", [])]

    if any(b in seller for b in blocked):
        return False

    if allowed:
        return any(a in seller for a in allowed)

    return True


def should_alert(product, store_config, result):
    print("DEBUG in_stock:", result.get("in_stock"))
    print("DEBUG price:", result.get("price"))
    print("DEBUG max_price:", product.get("max_price"))
    print("DEBUG seller:", result.get("seller"))
    print("DEBUG allowed_sellers:", store_config.get("allowed_sellers"))

    if not result.get("in_stock"):
        print("FAILED: not in stock")
        return False

    if result.get("price") is None:
        print("FAILED: no price")
        return False

    if result["price"] > product["max_price"]:
        print("FAILED: price too high")
        return False

    if not seller_allowed(result, store_config):
        print("FAILED: seller not allowed")
        return False

    print("PASSED: should alert")
    return True


def main():
    with open("products.json", "r") as f:
        products = json.load(f)

    for product in products:
        print(f"\nChecking {product['name']}...")

        for store_name, store_config in product["stores"].items():
            if store_name not in PROVIDERS:
                print(f"Skipping {store_name}: no provider yet")
                continue

            print(f"Checking {store_name}...")

            try:
                result = PROVIDERS[store_name](product, store_config)

                print("Result:", result)

                if should_alert(product, store_config, result):
                    print("ALERT!")
                    send_alert(product, result)
                else:
                    print("No alert.")

            except Exception as e:
                print(f"Error checking {store_name}: {e}")


if __name__ == "__main__":
    main()
