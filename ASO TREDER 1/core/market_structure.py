# ============================================
# DETECT REAL ACCUMULATION ZONES
# ============================================

def detect_accumulation(candles):

    zones = []

    checked_zones = []

    # ========================================
    # SCAN MARKET
    # ========================================

    for i in range(len(candles) - 15):

        # TAKE 15 CANDLES
        candle_group = candles[i:i + 15]

        highs = [c["high"] for c in candle_group]

        lows = [c["low"] for c in candle_group]

        closes = [c["close"] for c in candle_group]

        opens = [c["open"] for c in candle_group]

        zone_high = max(highs)

        zone_low = min(lows)

        range_size = zone_high - zone_low

        # ====================================
        # SMALL MOVEMENT = ACCUMULATION
        # ====================================

        if range_size < 0.0006:

            # =================================
            # FILTER DUPLICATES
            # =================================

            duplicate = False

            for zone in checked_zones:

                if abs(zone - zone_low) < 0.0003:

                    duplicate = True

                    break

            if duplicate:
                continue

            checked_zones.append(zone_low)

            # =================================
            # SAVE ZONE
            # =================================

            zones.append({

                "start_time":
                    candle_group[0]["datetime"],

                "end_time":
                    candle_group[-1]["datetime"],

                "high":
                    round(zone_high, 5),

                "low":
                    round(zone_low, 5),

                "range":
                    round(range_size, 5)
            })

    # ========================================
    # RETURN TOP ZONES
    # ========================================

    return zones[:10]