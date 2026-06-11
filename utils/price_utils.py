import re

def get_price(text):
    lower_text = text.lower()

    # Remove playment plan / financing sections
    bad_patterns = [
        r"\d+\spayments\s+starting\s+at\s+$[0-9]+(?:\.[0-9]{2})?",
        r"starting\s+at\s+\$[0-9]+(?:\.[0-9]{2})?",
        r"\$[0-9]+(?:\.[0-9]{2})?\s+with\s+zip",
        r"finance options.*",
    ]
    
    for pattern in bad_patterns:
        lower_text = re.sub(pattern, "", lower_text)
    
    prices = re.findall(r"\$([0-9]+(?:\.[0-9]{2})?)", lower_text)

    if not prices:
        return None
    
    prices = [float(price) for price in prices]
    
    realistic_prices = [
        price for price in prices
        if 5 <= price <= 300
    ]

    if not realistic_prices:
        return None
    
    return min(realistic_prices)