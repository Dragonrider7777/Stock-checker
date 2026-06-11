from utils.price_utils import get_price
from utils.stock_utils import get_stock_status

def check(page, product):
    page.goto(product["url"], wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timout(7000)

    text = page.inner_text("body")

    return {
        "price": get_price(text),
        "in_stock": get_stock_status(text),
        "marketplace": False
    }