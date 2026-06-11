from alerts.gmail_alert import send_gmail_alert
from alerts.discord_alert import send_discord_alert

def send_alert(product, result):
    send_gmail_alert(product, result)
    send_discord_alert(product, result)