import requests
import xml.etree.ElementTree as ET
import time

# Telegram Configuration
TELEGRAM_TOKEN = "8856307803:AAF31D7S0cMEf8xuFzbgnSwtkBMq-hsfJJE"
CHANNEL_ID = "@ipo_365"

def send_telegram_alert(text):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Sent! Response: {response.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

def fetch_and_post_ipos():
    # Stable Economic Times RSS feed for Indian IPOs
    rss_url = "https://indiatimes.com"
    try:
        response = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # Fetch latest 2 live updates
            for item in root.findall('./channel/item')[:2]: 
                title = item.find('title').text
                link = item.find('link').text
                
                message = (
                    f"🚨 *IPO 365 LIVE UPDATE* 🚨\n\n"
                    f"📈 *{title}*\n\n"
                    f"🔗 [Poori detail yahan padhein]({link})\n\n"
                    f"#IPO365 #IndianMarket"
                )
                send_telegram_alert(message)
                time.sleep(3)
    except Exception as e:
        print(f"Fetch error: {e}")

if __name__ == "__main__":
    fetch_and_post_ipos()
    
