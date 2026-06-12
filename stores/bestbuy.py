import re

from utils.stock_utils import get_stock_status
from utils.marketplace_utils import is_allowed_seller


def safe_goto(page, url, retries=3):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            return
        except Exception as e:
            last_error = e
            print(f"Best Buy navigation failed. Retry {attempt}/{retries}...")
            page.wait_for_timeout(3000)

    raise last_error


def verify_sku(text, sku):
    return str(sku) in text


def extract_price_near_seller(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    seller_index = None

    for i, line in enumerate(lines):
        lower = line.lower()

        if "sold & shipped by" in lower or "sold and shipped by" in lower:
            seller_index = i
            break

    if seller_index is None:
        return None, "No seller area found"

    nearby_lines = lines[seller_index : seller_index + 12]

    prices = []

    for line in nearby_lines:
        lower = line.lower()

        if "payment" in lower:
            continue

        if "starting at" in lower:
            continue

        if "zip" in lower:
            continue

        matches = re.findall(r"\$([0-9,]+(?:\.[0-9]{2})?)", line)

        for match in matches:
            price = float(match.replace(",", ""))

            if 10 <= price <= 300:
                prices.append(price)

    if not prices:
        return None, "No valid price found near seller area"

    return max(prices), "Found price near seller area"


def check(page, product):
    safe_goto(page, product["url"])
    page.wait_for_timeout(6000)

    text = page.inner_text("body")

    if not verify_sku(text, product["sku"]):
        raise Exception(f"SKU {product['sku']} not found. Wrong Best Buy page loaded.")

    price, price_reason = extract_price_near_seller(text)

    allowed, seller, seller_reason = is_allowed_seller(text, product)

    if seller is None:
        allowed = False
        seller_reason = "No seller found, unsafe"

    return {
        "price": price,
        "price_reason": price_reason,
        "in_stock": get_stock_status(text),
        "marketplace": not allowed,
        "seller": seller,
        "seller_reason": seller_reason,
        "product_url": page.url,
    }
