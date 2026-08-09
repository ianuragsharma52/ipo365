import os
import warnings
from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Handle optional local dotenv environments safely
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

warnings.filterwarnings("ignore")

# Production Credentials Management
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8856307803:AAF31D7S0cMEf8xuFzbgnSwtkBMq-hsfJJE")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL", "@ipo_365")


def send_telegram_message(message_text):
    """Transmits clean Markdown notification payloads to Telegram."""
    try:
        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHANNEL,
            "text": message_text,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, json=payload, timeout=12)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram dispatch failed: {e}")


def scrape_moneycontrol_data(url):
    """Scrapes operational listing metadata catalogs from Moneycontrol."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")
        upcoming_ipos_df = None
        mainboard_ipos_df = None

        for table in tables:
            if table.find("td", string="Upcoming"):
                upcoming_ipos_df = pd.read_html(str(table))[0]
                upcoming_ipos_df = upcoming_ipos_df.iloc[1:]
            elif table.find("td", string="Open"):
                mainboard_ipos_df = pd.read_html(str(table))[0]
                mainboard_ipos_df = mainboard_ipos_df.iloc[1:]

        if upcoming_ipos_df is not None and mainboard_ipos_df is not None:
            columns = [
                "Company Name", "Main_SME", "Issue Price", "Lot Size", "Issue Size",
                "Time Subscribed", "Open Date", "Close Date", "Allotment Date", "Listing Date"
            ]
            upcoming_ipos_df.columns = columns
            mainboard_ipos_df.columns = columns
            return pd.concat([upcoming_ipos_df, mainboard_ipos_df])

        print("Target tracking data arrays missing from Moneycontrol parse trees.")
        return None
    except Exception as e:
        print(f"Moneycontrol source ingestion failure: {str(e)}")
        return None


def scrape_live_gmp():
    """Extracts grey market premium data from InvestorGain."""
    try:
        url = "https://investorgain.com"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "mainTable"}) or soup.find("table")

        if not table:
            return None

        df = pd.read_html(str(table))[0]

        # Flatten dynamic Multi-Index schemas instantly
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ["_".join(col).strip() for col in df.columns.values]

        company_col = df.columns[0]
        gmp_col = [c for c in df.columns if "gmp" in c.lower()]
        gain_col = [c for c in df.columns if "profit" in c.lower() or "gain" in c.lower()]

        if not gmp_col or not gain_col:
            return None

        clean_df = df[[company_col, gmp_col[0], gain_col[0]]].copy()
        clean_df.columns = ["GMP_Company", "GMP_Value", "Est_Gain_Pct"]
        return clean_df
    except Exception as e:
        print(f"InvestorGain secondary index tracking bypassed: {e}")
        return None


def match_gmp_to_ipos(combined_df, gmp_df):
    """Stitches premium values across both web targets using string matching."""
    if gmp_df is None or gmp_df.empty:
        combined_df["GMP_Value"] = "N/A"
        combined_df["Est_Gain_Pct"] = "N/A"
        return combined_df

    gmp_values = []
    gain_pcts = []

    for _, row in combined_df.iterrows():
        comp_name = str(row["Company Name"]).lower().split("limited")[0].strip()
        matched_gmp = "N/A"
        matched_pct = "N/A"

        for _, gmp_row in gmp_df.iterrows():
            gmp_comp = str(gmp_row["GMP_Company"]).lower()
            if comp_name in gmp_comp or gmp_comp in comp_name:
                matched_gmp = str(gmp_row["GMP_Value"])
                matched_pct = str(gmp_row["Est_Gain_Pct"])
                break

        gmp_values.append(matched_gmp)
        gain_pcts.append(matched_pct)

    combined_df["GMP_Value"] = gmp_values
    combined_df["Est_Gain_Pct"] = gain_pcts
    return combined_df


def calculate_min_fund_required(combined_ipos_df, today, next_7_days_end):
    """Tracks capital allocation requirements over the operational lifecycle."""
    mainboard_ipos_df = combined_ipos_df[combined_ipos_df["Main_SME"] == "Mainline"].copy()

    if mainboard_ipos_df.empty:
        return 0, mainboard_ipos_df

    date_columns = ["Open Date", "Close Date", "Allotment Date", "Listing Date"]
    for col in date_columns:
        mainboard_ipos_df[col] = pd.to_datetime(mainboard_ipos_df[col], format="%d %b %y", errors="coerce")

    next_7_days_ipos = mainboard_ipos_df[
        (mainboard_ipos_df["Open Date"] >= today) & (mainboard_ipos_df["Open Date"] <= next_7_days_end)
    ].copy()

    if next_7_days_ipos.empty:
        return 0, next_7_days_ipos

    # Extract price cap structures safely (e.g., handles "₹100 - ₹105" patterns)
    prices = next_7_days_ipos["Issue Price"].astype(str).str.replace("₹", "").str.split("-").str[-1]
    next_7_days_ipos["Clean Price"] = pd.to_numeric(prices, errors="coerce")
    next_7_days_ipos["Clean Lot"] = pd.to_numeric(next_7_days_ipos["Lot Size"], errors="coerce")

    next_7_days_ipos["Fund Required"] = next_7_days_ipos["Clean Price"] * next_7_days_ipos["Clean Lot"]
    next_7_days_ipos["Unblock Date"] = next_7_days_ipos["Allotment Date"] + timedelta(days=1)

    daily_funds_blocked = {}
    for _, row in next_7_days_ipos.iterrows():
        open_date = row["Close Date"]
        unblock_date = row["Unblock Date"]
        fund_required = row["Fund Required"]

        if pd.isna(unblock_date) or pd.isna(open_date) or pd.isna(fund_required):
            continue

        current_date = open_date
        while current_date <= unblock_date:
            daily_funds_blocked[current_date] = daily_funds_blocked.get(current_date, 0) + fund_required
            current_date += timedelta(days=1)

    max_fund_required = max(daily_funds_blocked.values()) if daily_funds_blocked else 0
    return max_fund_required, next_7_days_ipos


def send_ipo_notifications(next_7_days_ipos, min_fund):
    """Formats and dispatches alerts directly into Telegram channel pipelines."""
    if next_7_days_ipos.empty:
        print("No active pipeline profiles identified inside tracing window.")
        return

    summary_msg = (
        f"📊 *IPO Capital Requirement Report*\n"
        f"Peak overlapping capital layout requirement needed over next 7 days: "
        f"*₹{min_fund:,.2f}*"
    )
    send_telegram_message(summary_msg)

    for _, row in next_7_days_ipos.iterrows():
        open_str = row["Open Date"].strftime("%Y-%m-%d") if not pd.isna(row["Open Date"]) else "TBD"
        close_str = row["Close Date"].strftime("%Y-%m-%d") if not pd.isna(row["Close Date"]) else "TBD"

        company_msg = (
            f"🚀 *New IPO Launch Alert*\n\n"
            f"🏢 *Company:* {row['Company Name']}\n"
            f"📅 *Open Date:* {open_str}\n"
            f"📅 *Close Date:* {close_str}\n"
            f"💰 *Issue Price:* {row['Issue Price']}\n"
            f"📦 *Lot Size:* {row['Lot Size']}\n"
            f"💸 *Total Issue Size:* {row['Issue Size']}\n"
            f"🔥 *GMP Today:* `{row['GMP_Value']}`\n"
            f"📈 *Estimated Listing Gain:* `{row['Est_Gain_Pct']}`"
        )
        send_telegram_message(company_msg)


if __name__ == "__main__":
    mc_url = "https://moneycontrol.com"
    try:
        raw_ipos = scrape_moneycontrol_data(mc_url)
        if raw_ipos is not None:
            raw_gmp = scrape_live_gmp()
            combined_data = match_gmp_to_ipos(raw_ipos, raw_gmp)

            start_today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            end_window = start_today + timedelta(days=6)

            peak_fund, filtered_df = calculate_min_fund_required(combined_data, start_today, end_window)
            send_ipo_notifications(filtered_df, peak_fund)
            print("Production cycle completed.")
    except Exception as main_error:
        print(f"Execution failure: {main_error}")
