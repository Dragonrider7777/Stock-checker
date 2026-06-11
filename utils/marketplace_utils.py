from config.settings import MARKETPLACE_WORDS

def has_marketplace(text):
    lower_text = text.lower()

    return any(word in lower_text for word in MARKETPLACE_WORDS)