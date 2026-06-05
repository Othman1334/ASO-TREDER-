# ============================================
# ASO TREDER - SIGNAL ENGINE
# ============================================

from core.probability_engine import validate_trade


def determine_entry_type(liquidity):
    if liquidity["liquidity_sweep"]:
        return "دخول بعد كنس سيولة"
    if liquidity["stop_hunt"]:
        return "دخول بعد صيد وقف"
    if liquidity["fake_breakout"]:
        return "دخول بعد اختراق كاذب"
    return "دخول سوق"


def determine_signal_direction(structure, smart_money):
    """
    Weighted bias: combine every available clue into bull vs bear score.
    Always resolves to CALL or PUT (no more permanent NO TRADE).
    """
    bull = 0
    bear = 0

    if structure["trend"] == "bullish": bull += 2
    elif structure["trend"] == "bearish": bear += 2

    if structure["bos"]:
        if structure["bos_direction"] == "bullish": bull += 2
        elif structure["bos_direction"] == "bearish": bear += 2

    inst = smart_money["institutional_candle"]
    if inst:
        if inst["type"] == "bullish_institutional": bull += 2
        else: bear += 2

    if smart_money["total_bullish_fvg"] > 0: bull += 1
    if smart_money["total_bearish_fvg"] > 0: bear += 1
    if smart_money["total_bullish_obs"] > 0: bull += 1
    if smart_money["total_bearish_obs"] > 0: bear += 1

    bull += structure.get("hh", 0) + structure.get("hl", 0)
    bear += structure.get("ll", 0) + structure.get("lh", 0)

    if bull > bear:
        direction = "CALL"
    elif bear > bull:
        direction = "PUT"
    elif structure["bos_direction"] == "bearish":
        direction = "PUT"
    else:
        direction = "CALL"

    return direction, bull, bear


def generate_signal(analysis):
    structure   = analysis["structure"]
    liquidity   = analysis["liquidity"]
    smart_money = analysis["smart_money"]
    confidence  = analysis["confidence"]
    reasons     = list(analysis["reasons"])
    risk        = analysis["risk"]

    direction, bull, bear = determine_signal_direction(structure, smart_money)
    entry_type = determine_entry_type(liquidity)

    if not reasons:
        reasons = ["إشارة مبنية على الاتجاه العام والزخم الحالي"]

    # المخاطرة تتبع نسبة الثقة مباشرة (متوافقة دائماً: ثقة عالية = مخاطرة منخفضة)
    # Alert (sound + toast) only for the better-quality setups
    alert = risk in ("LOW", "MEDIUM")

    return {
        "signal":     direction,
        "entry_type": entry_type,
        "expiry":     "دقيقتان",
        "confidence": confidence,
        "risk":       risk,
        "reasons":    reasons,
        "alert":      alert,
    }
