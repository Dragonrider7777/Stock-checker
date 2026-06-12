import re


def clean_price_string(price_text):
    return float(price_text.replace(",", ""))


def get_price(text):
    # Match prices like:
    # $114.95
    # $60
    # $1,299.99
    raw_prices = re.findall(r"\$([0-9,]+(?:\.[0-9]{2})?)", text)

    if not raw_prices:
        return None

    prices = []

    for raw_price in raw_prices:
        price = clean_price_string(raw_price)

        # Ignore tiny payment-plan numbers like $4.05, but keep real Pokemon product prices
        if 10 <= price <= 300:
            prices.append(price)

    if not prices:
        return None

    # Payment plans are usually smaller, real reseller price is usually largest on page
    return max(prices)
