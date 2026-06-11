import os
import requests

def send_discord_alert(product, result):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("Discord skipped. Missing DISCORD_WEBHOOK_URL")
        return
    
    message = f""" 
** POKEMON RESTOCK ALERT**

**{product['name']}**
Store: `{product['store']}`
Price: `${result['price']}`
Max price: `${product['max_price']}`

{product['url']}
"""
    
    requests.post(webhook_url, json={"content": message}, timeout=10)

    print("Discord alert sent.")