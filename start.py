import os
import requests
import yfinance as yf

# Aapka token aur channel handle direct code mein set hai
TOKEN = "8856307803:AAF31D7S0cMEf8xuFzbgnSwtkBMq-hsfJJE"
CHAT_ID = "@ipo_365"

def get_market_summary():
    """Fetches real-time closing data for Nifty 50 and BSE Sensex."""
    try:
        nifty = yf.Ticker("^NSEI").history(period="1d")['Close'].iloc[-1]
        sensex = yf.Ticker("^BSESN").history(period="1d")['Close'].iloc[-1]
        return f"📈 *INDICES MARKET UPDATE*\n\n🔹 *NIFTY 50:* {nifty:.2f}\n🔹 *BSE SENSEX:* {sensex:.2f}\n"
    except Exception as e:
        print(f"Error fetching market indices: {e}")
        return "📈 *INDICES MARKET UPDATE*\n\n⚠️ Market data currently unavailable.\n"

def get_ipo_summary():
    """Fetches ongoing and upcoming Indian IPO data from IPO Guru API."""
    try:
        url = "https://ipoguru.in" 
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            return "🚀 *IPO 365 UPDATES*\n\n⚠️ Live IPO dashboard feed data unavailable right now."
            
        data = response.json().get("data", [])
        active_ipos = [i for i in data if i.get("status", "").upper() in ["OPEN", "UPCOMING"]]
        
        if not active_ipos:
            return "🚀 *IPO 365 UPDATES*\n\n🟢 No active or upcoming Mainboard or SME IPOs found today."
            
        msg = "🚀 *IPO 365 - LIVE TRACKER (Mainboard & SME)* 🚀\n\n"
        for ipo in active_ipos[:6]:
            name = ipo.get("name", "Unknown Issue")
            category = ipo.get("category", "Mainboard")
            price_range = ipo.get("price_band", "N/A")
            gmp = ipo.get("gmp", "N/A")
            close_date = ipo.get("close_date", "N/A")
            
            msg += f"📦 *{name}* ({category})\n"
            msg += f"💰 Price Band: ₹{price_range}\n"
            msg += f"🔥 Current GMP: ₹{gmp}\n"
            msg += f"📅 Closes On: {close_date}\n"
            msg += "────────────────────────\n\n"
            
        return msg
    except Exception as e:
        print(f"Error fetching IPO updates: {e}")
        return "🚀 *IPO 365 UPDATES*\n\n⚠️ Error reading the regional financial tracker API feed."

def broadcast_to_channel():
    """Combines metrics and posts directly into the Telegram channel."""
    market_text = get_market_summary()
    ipo_text = get_ipo_summary()
    
    final_broadcast = f"{market_text}\n────────────────────────\n\n{ipo_text}"
    final_broadcast += "\n👉 Join @ipo_365 for regular financial updates!"
    
    telegram_url = f"https://telegram.org{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": final_broadcast,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    response = requests.post(telegram_url, json=payload)
    if response.status_code == 200:
        print("Channel broadcast successfully updated!")
    else:
        print(f"Broadcast failure status: {response.text}")

if __name__ == "__main__":
    broadcast_to_channel()
            
