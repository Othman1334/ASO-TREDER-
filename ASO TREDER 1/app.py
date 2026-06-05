# ============================================
# ASO TREDER - MAIN SERVER
# ⚜️ASO TREDER⚜️
# ============================================

from functools import wraps
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for
)
from core.candle_fetcher import fetch_candles, FOREX_PAIRS, TV_SYMBOLS
from core.analyzer import analyze_market

app = Flask(__name__)

# IMPORTANT: change this to your own long, random, secret value
# (and keep it private). It is used to sign the login session.
app.secret_key = "CHANGE-ME-TO-A-LONG-RANDOM-SECRET-9f3a8b1c7e"

VALID_LICENSES = [
    "ASO-TRD-7X92-KLM1",
    "ASO-TRD-4P81-ZXT5",
    "ASO-TRD-9Q73-HJK2",
    "ASO-TRD-6M24-RTY8",
    "ASO-TRD-8N15-WER4",
    "ASO-TRD-3B67-PLK9",
    "ASO-TRD-5C48-XCV7",
    "ASO-TRD-2D39-ASD6",
    "ASO-TRD-1F84-QWE3",
    "ASO-TRD-0G52-ZXC1",
    "ASO-TRD-4J21-UIP8",
    "ASO-TRD-8K64-MNB2",
    "ASO-TRD-6L37-VFR9",
    "ASO-TRD-9Z18-TGB4"
]


# ============================================
# AUTH GUARD
# ============================================

def login_required(view):
    """Block any access unless the session has a valid activated license."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("licensed"):
            # For API calls return JSON 401, for pages redirect to license page
            if request.path.startswith("/analyze"):
                return jsonify({"error": "Unauthorized — license required"}), 401
            return redirect(url_for("home"))
        return view(*args, **kwargs)
    return wrapped


# ============================================
# HOME - LICENSE PAGE
# ============================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================
# LICENSE ACTIVATION
# ============================================

@app.route("/activate", methods=["POST"])
def activate():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received"
            })

        # الحصول على المفتاح من الطلب
        key = str(data.get("licenseKey", "")).strip().upper()

        # مقارنة بدون حساسية للأحرف
        valid_keys = [k.upper() for k in VALID_LICENSES]

        if key in valid_keys:
            session["licensed"] = True

            return jsonify({
                "success": True,
                "message": "License Activated Successfully"
            })

        return jsonify({
            "success": False,
            "message": "Invalid License Key"
        })

    except Exception as e:
        print("LICENSE ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
# ============================================
# LOGOUT
# ============================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ============================================
# DASHBOARD  (PROTECTED)
# ============================================

@app.route("/dashboard")
@login_required
def dashboard():
    pairs = [{"label": p, "tv": TV_SYMBOLS[p]} for p in FOREX_PAIRS]
    return render_template("dashboard.html", pairs=pairs)


# ============================================
# ANALYZE ENDPOINT  (PROTECTED)
# ============================================

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    data   = request.get_json()
    pair   = data.get("pair", "EUR/USD")
    candle_count = int(data.get("candles", 500))

    candles, error = fetch_candles(pair, outputsize=candle_count)

    if error or not candles:
        return jsonify({"error": error or "No data returned"})

    analysis = analyze_market(candles)

    current_price = candles[-1]["close"]
    round_number  = round(current_price * 100) / 100

    return jsonify({
        "pair":        pair,
        "candles":     candle_count,
        "signal":      analysis.get("signal", "NO TRADE"),
        "confidence":  analysis.get("confidence", 0),
        "risk":        analysis.get("risk", "HIGH"),
        "entry_type":  analysis.get("entry_type", "WAIT"),
        "expiry":      analysis.get("expiry", "NONE"),
        "entry_price": round(current_price, 5),
        "round_number": round_number,
        "alert":       analysis.get("alert", False),
        "reasons":     analysis.get("reasons", []),

        # Structure
        "trend":           analysis["structure"]["trend"].upper(),
        "bos":             analysis["structure"]["bos"],
        "bos_direction":   analysis["structure"].get("bos_direction", ""),
        "choch":           analysis["structure"]["choch"],
        "market_strength": analysis["structure"]["market_strength"].upper(),
        "strength_pct":    analysis["structure"]["strength_pct"],
        "hh": analysis["structure"]["hh"],
        "hl": analysis["structure"]["hl"],
        "ll": analysis["structure"]["ll"],
        "lh": analysis["structure"]["lh"],

        # Liquidity
        "liquidity_sweep":  analysis["liquidity"]["liquidity_sweep"],
        "stop_hunt":        analysis["liquidity"]["stop_hunt"],
        "fake_breakout":    analysis["liquidity"]["fake_breakout"],
        "equal_highs":      analysis["liquidity"]["total_equal_highs"],
        "equal_lows":       analysis["liquidity"]["total_equal_lows"],

        # Smart Money
        "institutional_candle":  analysis["smart_money"]["institutional_candle"],
        "total_bullish_fvg":     analysis["smart_money"]["total_bullish_fvg"],
        "total_bearish_fvg":     analysis["smart_money"]["total_bearish_fvg"],
        "total_bullish_obs":     analysis["smart_money"]["total_bullish_obs"],
        "total_bearish_obs":     analysis["smart_money"]["total_bearish_obs"],
        "breaker_blocks":        len(analysis["smart_money"]["breaker_blocks"]),
        "imbalances":            len(analysis["smart_money"]["imbalances"]),
    })


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
