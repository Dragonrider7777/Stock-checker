import re


def find_seller(text):
    patterns = [
        r"sold\s*&\s*shipped\s*by\s+([A-Za-z0-9 &.-]+)",
        r"sold\s+and\s+shipped\s+by\s+([A-Za-z0-9 &.-]+)",
        r"sold\s+by\s+([A-Za-z0-9 &.-]+)",
        r"ships\s+from\s+and\s+sold\s+by\s+([A-Za-z0-9 &.-]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            seller = match.group(1).strip()
            seller = seller.split("\n")[0].strip()
            return seller

    return None


def is_allowed_seller(text, product):
    seller = find_seller(text)

    allowed_sellers = [
        seller.lower()
        for seller in product.get("allowed_sellers", [])
    ]

    blocked_sellers = [
        seller.lower()
        for seller in product.get("blocked_sellers", [])
    ]

    if seller is None:
        return True, None, "No seller found"

    seller_lower = seller.lower()

    for blocked in blocked_sellers:
        if blocked in seller_lower:
            return False, seller, "Blocked seller"

    if allowed_sellers:
        for allowed in allowed_sellers:
            if allowed in seller_lower:
                return True, seller, "Allowed seller"

        return False, seller, "Seller not in allowed list"

    return True, seller, "No allowed seller restriction"