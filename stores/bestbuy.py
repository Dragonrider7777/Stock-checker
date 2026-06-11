from utils.price_utils import get_price
from utils.stock_utils import get_stock_status
from utils.marketplace_utils import is_allowed_seller


def check(page, product):
    page.goto(product["url"], wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    text = page.inner_text("body")

    allowed, seller, seller_reason = is_allowed_seller(text, product)

    return {
        "price": get_price(text),
        "in_stock": get_stock_status(text),
        "marketplace": not allowed,
        "seller": seller,
        "seller_reason": seller_reason
    }