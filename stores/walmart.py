import re

from utils.stock_utils import get_stock_status


def safe_goto(page, url, retries=3):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            return
        except Exception as e:
            last_error = e
            print(f"Walmart navigation failed. Retry {attempt}/{retries}...")
            page.wait_for_timeout(3000)

    raise last_error


def verify_item_id(page, text, item_id):
    item_id = str(item_id)
    html = page.content()

    return item_id in page.url or item_id in text or item_id in html


def evaluate_seller(seller, product):
    seller_lower = seller.lower()

    allowed_sellers = [s.lower() for s in product.get("allowed_sellers", [])]
    blocked_sellers = [s.lower() for s in product.get("blocked_sellers", [])]

    if any(blocked in seller_lower for blocked in blocked_sellers):
        return False, seller, "Blocked seller"

    if any(allowed in seller_lower for allowed in allowed_sellers):
        return True, seller, "Allowed seller"

    return False, seller, "Seller not in allowed list"


def extract_walmart_seller(text, product):
    patterns = [
        r"sold and shipped by\s+([^\n]+)",
        r"sold by\s+([^\n]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            seller = match.group(1).strip()
            return evaluate_seller(seller, product)

    return False, None, "No seller found, unsafe"


def extract_walmart_price(text):
    prices = re.findall(r"\$([0-9,]+(?:\.[0-9]{2})?)", text)

    valid_prices = []

    for raw_price in prices:
        price = float(raw_price.replace(",", ""))

        if 5 <= price <= 500:
            valid_prices.append(price)

    if not valid_prices:
        return None, "No valid Walmart price found"

    return max(valid_prices), "Found Walmart price from page text"


def check(page, product):
    safe_goto(page, product["url"])
    page.wait_for_timeout(7000)

    text = page.inner_text("body")

    if product.get("item_id") and not verify_item_id(page, text, product["item_id"]):
        print(f"Final Walmart URL: {page.url}")
        raise Exception(
            f"Item ID {product['item_id']} not found. Wrong Walmart page loaded."
        )

    price, price_reason = extract_walmart_price(text)
    allowed, seller, seller_reason = extract_walmart_seller(text, product)

    return {
        "price": price,
        "price_reason": price_reason,
        "in_stock": get_stock_status(text),
        "marketplace": not allowed,
        "seller": seller,
        "seller_reason": seller_reason,
        "product_url": page.url,
    }
