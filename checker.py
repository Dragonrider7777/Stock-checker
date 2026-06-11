from playwright.sync_api import sync_playwright
from utils.json_utils import load_products
from stock_manager import process_product


def main():
    products = load_products()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for product in products:
            process_product(page, product)

        browser.close()


if __name__ == "__main__":
    main()
