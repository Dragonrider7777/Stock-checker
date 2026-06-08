import json
import os
import re
import smtplib
import time
from email.message import EmailMessage
from playwright.sync_api import sync_playwright


def send_email_alert(product_name, url, price):
    sender = os.environ["sona.ramratnam@gmail.com"]
    password = os.environ["mszy lprb yffh juxc"]
    recipient = os.environ["sona.ramratnam@gmail.com"]

    msg = EmailMessage()
    msg["Subject"] = f"Pokemon Restock Alert: {product_name}"
    msg["From"] = sender
    msg["To"] = recipient

    msg.set_content(
        f"{product_name} may be in stock!\n\n"
        f"Price: ${price}\n"
        f"Link: {url}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)


def convert_price(price_text):
    match = re.search(r"\$([0-9]+(?:\.[0-9]{2})?)", price_text)

    if match is None:
        return None

    return float(match.group(1))


def get_prices(page):
    price_texts = page.locator("text=/\\$\\d+(\\.\\d{2})?/").all_inner_texts()

    prices = []

    for price_text in price_texts:
        price = convert_price(price_text)

        if price is not None:
            prices.append(price)

    return prices


def get_lowest_price(page):
    prices = get_prices(page)

    if not prices:
        return None

    return min(prices)


def is_best_buy_in_stock(page):
    buttons = page.locator("button").all_inner_texts()
    button_text = " ".join(buttons).lower()

    return "add to cart" in button_text


def check_product(page, product):
    print(f"\nChecking {product['name']}...")

    page.goto(product["url"], wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)

    store = product.get("store", "").lower()
    max_price = product.get("max_price")

    price = get_lowest_price(page)

    if price is not None:
        print(f"Lowest price found: ${price}")
    else:
        print("No price found.")

    if max_price is not None and price is not None and price > max_price:
        print(f"Too expensive: ${price} > ${max_price}")
        return False, price

    if store == "best buy":
        in_stock = is_best_buy_in_stock(page)
    else:
        text = page.locator("body").inner_text().lower()
        in_stock = "add to cart" in text or "in stock" in text

    return in_stock, price


def main():
    with open("products.json", "r") as file:
        products = json.load(file)

    found_anything = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for product in products:
            try:
                in_stock, price = check_product(page, product)

                if in_stock:
                    print(f"IN STOCK: {product['name']}")
                    send_email_alert(product["name"], product["url"], price)
                    found_anything = True
                else:
                    print(f"Out of stock: {product['name']}")

            except Exception as e:
                print(f"Error checking {product['name']}: {e}")

        browser.close()

    if not found_anything:
        print("\nNo good restocks found.")


if __name__ == "__main__":
    main()