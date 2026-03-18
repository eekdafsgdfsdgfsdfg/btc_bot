#!/usr/bin/env python3
"""
BTC Price Telegram Bot
Runs once per execution — designed for GitHub Actions (scheduled every 5 min).
"""

import requests
import os
from datetime import datetime

# ── CONFIG (read from GitHub Secrets) ───────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")
# ────────────────────────────────────────────────────────

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN and CHAT_ID must be set as environment variables / GitHub Secrets.")


def get_btc_price():
    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return float(r.json()["data"]["amount"])


def get_btc_stats():
    try:
        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            "?ids=bitcoin&vs_currencies=usd"
            "&include_24hr_high=true&include_24hr_low=true&include_24hr_change=true"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()["bitcoin"]
        return data.get("usd_24h_high"), data.get("usd_24h_low"), data.get("usd_24h_change")
    except Exception:
        return None, None, None


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()


def run():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    price = get_btc_price()
    high24, low24, change24 = get_btc_stats()

    arrow = "🟢" if (change24 or 0) >= 0 else "🔴"
    stats_lines = ""
    if high24 and low24:
        stats_lines = (
            f"\n📈 24h High:   <b>${high24:,.2f}</b>"
            f"\n📉 24h Low:    <b>${low24:,.2f}</b>"
        )
    if change24 is not None:
        stats_lines += f"\n{arrow} 24h Change: <b>{'+' if change24 >= 0 else ''}{change24:.2f}%</b>"

    msg = (
        f"₿ <b>BTC / USD</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💵 Price: <b>${price:,.2f}</b>"
        f"{stats_lines}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🕐 {now}"
    )
    send_message(msg)
    print(f"✅ Sent BTC price: ${price:,.2f}")


if __name__ == "__main__":
    run()
