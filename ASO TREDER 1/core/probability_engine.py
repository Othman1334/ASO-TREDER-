# ============================================
# ASO TREDER - PROBABILITY ENGINE
# ============================================

def score_structure(structure):
    score = 0
    reasons = []
    if structure["trend"] != "neutral":
        score += 20
        reasons.append("هيكل سوق صاعد" if structure["trend"] == "bullish" else "هيكل سوق هابط")
    if structure["bos"]:
        score += 20
        reasons.append(f"كسر هيكل ({'صاعد' if structure['bos_direction']=='bullish' else 'هابط'})")
    if not structure["choch"]:
        score += 10
    else:
        score -= 10
        reasons.append("⚠️ تغيّر طابع السوق (CHOCH)")
    if structure["market_strength"] == "strong":
        score += 15
        reasons.append(f"جسم شمعة قوي ({structure['strength_pct']}%)")
    elif structure["market_strength"] == "medium":
        score += 8
    hh = structure.get("hh", 0); hl = structure.get("hl", 0)
    ll = structure.get("ll", 0); lh = structure.get("lh", 0)
    if structure["trend"] == "bullish" and hh >= 2 and hl >= 2:
        score += 10
        reasons.append(f"قمم وقيعان صاعدة مؤكدة (HH×{hh} + HL×{hl})")
    if structure["trend"] == "bearish" and ll >= 2 and lh >= 2:
        score += 10
        reasons.append(f"قمم وقيعان هابطة مؤكدة (LL×{ll} + LH×{lh})")
    return score, reasons


def score_liquidity(liquidity):
    score = 0
    reasons = []
    if liquidity["liquidity_sweep"]:
        score += 20
        sw = liquidity["liquidity_sweep"]
        reasons.append(f"كنس سيولة عند {sw['level']}")
    if liquidity["stop_hunt"]:
        score += 15
        reasons.append(f"صيد وقف خسارة: {liquidity['stop_hunt']['description']}")
    if liquidity["fake_breakout"]:
        score += 10
        reasons.append(f"اختراق كاذب: {liquidity['fake_breakout']['description']}")
    if liquidity["inducement"]:
        score += 8
        reasons.append(f"استدراج: {liquidity['inducement']['description']}")
    if liquidity["total_equal_highs"] >= 2:
        score += 5
        reasons.append(f"تجمّع قمم متساوية ({liquidity['total_equal_highs']})")
    if liquidity["total_equal_lows"] >= 2:
        score += 5
        reasons.append(f"تجمّع قيعان متساوية ({liquidity['total_equal_lows']})")
    return score, reasons


def score_smart_money(smart_money):
    score = 0
    reasons = []
    if smart_money["institutional_candle"]:
        score += 20
        ic = smart_money["institutional_candle"]
        reasons.append(f"شمعة مؤسسية (جسم {ic['body_ratio']}%، {ic['size_vs_avg']}× المعدل)")
    if smart_money["total_bullish_fvg"] > 0:
        score += 10
        reasons.append(f"فجوة سعرية صاعدة ×{smart_money['total_bullish_fvg']}")
    if smart_money["total_bearish_fvg"] > 0:
        score += 10
        reasons.append(f"فجوة سعرية هابطة ×{smart_money['total_bearish_fvg']}")
    if smart_money["total_bullish_obs"] > 0:
        score += 8
        reasons.append(f"أوردر بلوك صاعد ×{smart_money['total_bullish_obs']}")
    if smart_money["total_bearish_obs"] > 0:
        score += 8
        reasons.append(f"أوردر بلوك هابط ×{smart_money['total_bearish_obs']}")
    if smart_money["breaker_blocks"]:
        score += 7
        reasons.append("بلوك كاسر فعّال")
    if smart_money["imbalances"]:
        score += 5
        reasons.append(f"اختلال سعري ×{len(smart_money['imbalances'])}")
    return score, reasons


def calculate_confidence(structure, liquidity, smart_money):
    s1, r1 = score_structure(structure)
    s2, r2 = score_liquidity(liquidity)
    s3, r3 = score_smart_money(smart_money)
    raw = s1 + s2 + s3
    # base floor so weak setups still register a workable confidence
    confidence = max(min(raw, 100), 25)
    all_reasons = r1 + r2 + r3
    return confidence, all_reasons


def calculate_risk(confidence):
    # المخاطرة تعكس نسبة الثقة مباشرة
    # ثقة عالية = مخاطرة منخفضة (والعكس)
    if confidence >= 80: return "LOW"      # منخفضة
    if confidence >= 55: return "MEDIUM"   # متوسطة
    return "HIGH"                          # عالية


def validate_trade(structure, liquidity, smart_money, confidence):
    """
    Relaxed filter: we (almost) always return a tradable signal now.
    Setup quality is reflected through the RISK level instead of blocking.
    """
    return True, "Valid"
