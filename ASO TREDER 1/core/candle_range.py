# ============================================
# TRADIR AI - FOREX CANDLE ANALYZER
# FILE: core/candle_range.py
# ============================================

import requests


# ============================================
# TWELVEDATA API CONFIG
# ============================================

API_KEY = "45f3103dd4c64e57ad69421b29cd3e30"

BASE_URL = "https://api.twelvedata.com/time_series"


# ============================================
# FOREX PAIRS
# ============================================

FOREX_PAIRS = [

    # MAJOR PAIRS
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "USD/CHF",
    "AUD/USD",
    "USD/CAD",
    "NZD/USD",

    # MINOR PAIRS
    "EUR/GBP",
    "EUR/JPY",
    "EUR/AUD",
    "EUR/CAD",
    "GBP/JPY",
    "GBP/AUD",
    "GBP/CAD",
    "AUD/JPY",
    "CAD/JPY",
    "CHF/JPY",
    "NZD/JPY",

    # EXTRA PAIRS
    "EUR/CHF",
    "AUD/CAD",
    "AUD/CHF",
    "GBP/CHF",
    "NZD/CAD",
    "NZD/CHF"
]


# ============================================
# SHOW FOREX PAIRS
# ============================================

def show_pairs():

    print("\n===================================")
    print("AVAILABLE FOREX PAIRS")
    print("===================================\n")

    for index, pair in enumerate(FOREX_PAIRS, start=1):

        print(f"{index}. {pair}")

    print("\n===================================\n")


# ============================================
# FETCH LAST 500 CANDLES
# ============================================

def fetch_candles(

    symbol,

    interval="1min",

    outputsize=500
):

    params = {

        "symbol": symbol,

        "interval": interval,

        "outputsize": outputsize,

        "apikey": API_KEY
    }

    try:

        response = requests.get(

            BASE_URL,

            params=params
        )

        data = response.json()

        candles = []

        # ====================================
        # ERROR CHECK
        # ====================================

        if "values" not in data:

            print("\n===================================")
            print("ERROR FETCHING DATA")
            print("===================================\n")

            print(data)

            return []

        # ====================================
        # REVERSE DATA
        # ====================================

        values = list(reversed(data["values"]))

        # ====================================
        # BUILD CANDLES
        # ====================================

        for candle in values:

            candles.append({

                "datetime": candle["datetime"],

                "open": float(candle["open"]),

                "high": float(candle["high"]),

                "low": float(candle["low"]),

                "close": float(candle["close"])
            })

        return candles

    except Exception as error:

        print("\n===================================")
        print("FETCH ERROR")
        print("===================================\n")

        print(error)

        return []


# ============================================
# SAVE ALL CANDLES TO TXT FILE
# ============================================

def save_candles_to_file(

    pair,

    candles
):

    file_name = "candles_output.txt"

    with open(

        file_name,

        "w",

        encoding="utf-8"

    ) as file:

        file.write(
            "===================================\n"
        )

        file.write(
            "TRADIR AI - FOREX ANALYSIS\n"
        )

        file.write(
            "===================================\n\n"
        )

        file.write(
            f"PAIR: {pair}\n"
        )

        file.write(
            "TIMEFRAME: 1 MINUTE\n"
        )

        file.write(
            f"TOTAL CANDLES: {len(candles)}\n\n"
        )

        # ================================
        # WRITE ALL CANDLES
        # ================================

        for index, candle in enumerate(candles, start=1):

            file.write(
                f"========== CANDLE {index} ==========\n\n"
            )

            file.write(
                f"TIME:\n{candle['datetime']}\n\n"
            )

            file.write(
                f"OPEN:\n{candle['open']}\n\n"
            )

            file.write(
                f"HIGH:\n{candle['high']}\n\n"
            )

            file.write(
                f"LOW:\n{candle['low']}\n\n"
            )

            file.write(
                f"CLOSE:\n{candle['close']}\n\n"
            )

            file.write(
                "===================================\n\n"
            )

    print("\n===================================")
    print("500 CANDLES SAVED SUCCESSFULLY")
    print("FILE: candles_output.txt")
    print("===================================\n")


# ============================================
# ANALYZE PAIR
# ============================================

def analyze_pair(pair):

    print("\n===================================")
    print(f"FETCHING 500 CANDLES FOR {pair}")
    print("===================================\n")

    candles = fetch_candles(pair)

    if not candles:

        print("NO CANDLES FOUND")

        return

    # ====================================
    # SAVE FILE
    # ====================================

    save_candles_to_file(

        pair,

        candles
    )


# ============================================
# MAIN SYSTEM
# ============================================

if __name__ == "__main__":

    # SHOW FOREX PAIRS
    show_pairs()

    try:

        # USER SELECT
        choice = int(

            input("SELECT PAIR NUMBER: ")
        )

        # VALIDATE
        if choice < 1 or choice > len(FOREX_PAIRS):

            print("\nINVALID PAIR NUMBER\n")

        else:

            # GET PAIR
            selected_pair = FOREX_PAIRS[choice - 1]

            # RUN ANALYSIS
            analyze_pair(selected_pair)

    except ValueError:

        print("\nPLEASE ENTER A VALID NUMBER\n")