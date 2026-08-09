import requests

TELEGRAM_TOKEN = "8856307803:AAF31D7S0cMEf8xuFzbgnSwtkBMq-hsfJJE"
CHANNEL_ID = "@ipo_365"

def send_telegram_alert(text):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Final Server Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def fetch_and_post_ipos():
    try:
        message = (
            "🚨 IPO 365 AUTOMATION ACTIVE 🚨\n\n"
            "Indian IPO Market Updates System Live.\n\n"
            "Aapka automated channel successfully live ho gaya hai. Ab background system background mein IPO updates bhejna shuru kar dega!"
        )
        send_telegram_alert(message)
    except Exception as e:
        print(f"System error: {e}")

if __name__ == "__main__":
    fetch_and_post_ipos()
