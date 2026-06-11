from utils.price_utils import get_price
from utils.stock_utils import get_stock_status
from utils.marketplace_utils import is_allowed_seller


def build_search_url(product):
    return f"https://www.bestbuy.com/site/searchpage.jsp?" f"st={product['sku']}"


def check(page, product):
    search_url = build_search_url(product)

    page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

    page.wait_for_timeout(3000)

    product_link = page.locator("a.product-title-link").first

    if product_link.count() == 0:
        raise Exception(f"No product found for SKU {product['sku']}")

    href = product_link.get_attribute("href")

    product_url = "https://www.bestbuy.com" + href

    page.goto(product_url, wait_until="domcontentloaded", timeout=60000)

    page.wait_for_timeout(5000)

    text = page.inner_text("body")

    allowed, seller, seller_reason = is_allowed_seller(text, product)

    return {
        "price": get_price(text),
        "in_stock": get_stock_status(text),
        "marketplace": not allowed,
        "seller": seller,
        "seller_reason": seller_reason,
        "product_url": product_url,
    }
