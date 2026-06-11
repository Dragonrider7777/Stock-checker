from config.settings import IN_STOCK_WORDS, OUT_OF_STOCK_WORDS

def get_stock_status(text):
    lower_text = text.lower()

    out_of_stock = any(word in lower_text for word in OUT_OF_STOCK_WORDS)
    in_stock = any(word in lower_text for word in IN_STOCK_WORDS)

    if out_of_stock:
        return False
    
    if in_stock:
        return True
    
    return False