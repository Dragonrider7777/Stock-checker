import json
import re
from bs4 import BeautifulSoup
from seleniumbase import sb_cdp
from playwright.sync_api import sync_playwright


def find_values(obj, target_key):
    results = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == target_key:
                results.append(value)
            results.extend(find_values(value, target_key))

    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_values(item, target_key))

    return results


def parse_price(value):
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        match = re.search(r"\d+(?:\.\d+)?", value.replace(",", ""))
        if match:
            return float(match.group())

    return None


def check_walmart(product, store_config):
    url = store_config["url"]
    sb = None

    try:
        sb = sb_cdp.Chrome(locale="en", guest=True)
        sb.goto(url)

        endpoint_url = sb.get_endpoint_url()

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(endpoint_url)

            if not browser.contexts or not browser.contexts[0].pages:
                raise Exception("Could not connect to Walmart browser page")

            page = browser.contexts[0].pages[0]

            page.wait_for_timeout(2000)

            final_url = page.url
            html = page.content()

            if "robot or human" in html.lower() or "blocked" in final_url.lower():
                input("Solve the Walmart bot check, then press ENTER here...")
                page.wait_for_timeout(2000)
                html = page.content()
                final_url = page.url

            browser.close()

        lowered = html.lower()

        if "robot or human" in lowered or "blocked" in final_url:
            raise Exception("Walmart bot check / blocked page detected")

        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")

        if not script or not script.string:
            raise Exception("Could not find Walmart __NEXT_DATA__ JSON")

        data = json.loads(script.string)

        prices = find_values(data, "price")
        sellers = (
            find_values(data, "sellerName")
            + find_values(data, "sellerDisplayName")
            + find_values(data, "seller")
        )
        availabilities = find_values(data, "availabilityStatus")

        price = None
        for p in prices:
            parsed = parse_price(p)
            if parsed is not None:
                price = float(p)
                break

        seller = next((s for s in sellers if s), "Unknown")
        availability = str(availabilities[0]).lower() if availabilities else ""

        in_stock = any(
            word in availability
            for word in [
                "in_stock",
                "available",
                "available_online",
                "available for delivery",
            ]
        )

        return {
            "name": product["name"],
            "store": "Walmart",
            "price": price,
            "in_stock": in_stock,
            "url": url,
            "seller": seller,
            "raw_availability": availability,
        }

    finally:
        if sb is not None:
            try:
                sb.quit()
            except Exception:
                pass
