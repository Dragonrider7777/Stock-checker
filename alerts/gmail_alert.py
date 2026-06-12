import os
import smtplib
from email.message import EmailMessage


def send_gmail_alert(product, result):
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_to = os.getenv("EMAIL_TO")

    if not email_user or not email_password or not email_to:
        print("Gmail skipped. Missing email environment variables.")
        print("EMAIL_USER found:", email_user is not None)
        print("EMAIL_PASSWORD found:", email_password is not None)
        print("EMAIL_TO found:", email_to is not None)
        return

    subject = f"Pokemon Stock Alert: {product['name']}"

    body = f"""
{product['name']} is worth checking!

Store: {result['store']}
Price: ${result['price']}
Max price: ${product['max_price']}
Seller: {result.get('seller', 'Unknown')}

Link:
{result['url']}
"""

    msg = EmailMessage()
    msg["From"] = email_user
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_user, email_password)
            smtp.send_message(msg)

        print("Gmail alert sent.")

    except Exception as e:
        print(f"Failed to send Gmail alert: {e}")
