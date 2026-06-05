# ============================================
# TRADIR AI - CANDLE FETCHER
# ============================================

import requests

API_KEY  = "45f3103dd4c64e57ad69421b29cd3e30"
BASE_URL = "https://api.twelvedata.com/time_series"

FOREX_PAIRS = [
    "EUR/USD","GBP/USD","USD/JPY","USD/CHF","AUD/USD","USD/CAD","NZD/USD",
    "EUR/GBP","EUR/JPY","EUR/AUD","EUR/CAD","GBP/JPY","GBP/AUD","GBP/CAD",
    "AUD/JPY","CAD/JPY","CHF/JPY","NZD/JPY","EUR/CHF","AUD/CAD","AUD/CHF",
    "GBP/CHF","NZD/CAD","NZD/CHF"
]

# TradingView symbol format mapping
TV_SYMBOLS = {p: f"FX:{p.replace('/', '')}" for p in FOREX_PAIRS}


def fetch_candles(symbol, interval="1min", outputsize=500):
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": API_KEY
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        data = resp.json()
        if "values" not in data:
            return None, data.get("message", "API Error")
        values = list(reversed(data["values"]))
        candles = []
        for c in values:
            candles.append({
                "datetime": c["datetime"],
                "open":     float(c["open"]),
                "high":     float(c["high"]),
                "low":      float(c["low"]),
                "close":    float(c["close"]),
            })
        return candles, None
    except Exception as e:
        return None, str(e)
