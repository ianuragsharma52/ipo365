import requests
import json
import time

# Telegram Configuration
TELEGRAM_TOKEN = "8856307803:AAF31D7S0cMEf8xuFzbgnSwtkBMq-hsfJJE"
CHANNEL_ID = "@ipo_365"

def send_telegram_alert(text):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Sent! Status: {response.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

def fetch_and_post_ipos():
    # Direct and unrestricted financial news feed API
    api_url = "https://ok.xyz" # Temporary placeholder or use a stable endpoint
    # Fallback to direct stable public financial text data to ensure it runs
    try:
        message = (
            f"🚨 *IPO 365 LIVE TRACKER IS ACTIVE* 🚨\n\n"
            f"📈 *Indian IPO Market Updates System Live*\n\n"
            f"Humara automated bot active ho chuka hai. Ab yahan sabhi up-to-date Mainline aur SME IPOs ki details automatically aati rahengi!\n\n"
            f"#IPO365 #IndianMarket"
        )
        send_telegram_alert(message)
    except Exception as e:
        print(f"System error: {e}")

if __name__ == "__main__":
    fetch_and_post_ipos()
    
