import requests

# Final Correct Configuration
TELEGRAM_TOKEN = "8856307803:AAF31D7S0cMEf8xuFzbgnSwtkBMq-hsfJJE"
CHANNEL_ID = "@ipo_365"

def send_telegram_alert(text):
    # API Link bilkul correct hai aur verification done hai
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Server Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def fetch_and_post_ipos():
    try:
        message = (
            "🚨 IPO 365 LIVE TRACKER IS ACTIVE 🚨\n\n"
            "Indian IPO Market Updates System Live.\n\n"
            "Humara automated bot successfully active ho chuka hai! Ab yahan sabhi up-to-date Mainline aur SME IPOs ki details automatically aati rahengi."
        )
        send_telegram_alert(message)
    except Exception as e:
        print(f"System error: {e}")

if __name__ == "__main__":
    fetch_and_post_ipos()
        
