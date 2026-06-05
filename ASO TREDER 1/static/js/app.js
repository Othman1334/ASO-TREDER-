// ============================================
// ⚜️ ASO TREDER ⚜️ — app.js
// ============================================

// ── خرائط الترجمة للعرض ──────────────────────
const T_SIGNAL = { "CALL": "شراء", "PUT": "بيع", "NO TRADE": "لا صفقة" };
const T_RISK   = { "LOW": "منخفضة", "MEDIUM": "متوسطة", "HIGH": "عالية" };
const T_TREND  = { "BULLISH": "صاعد", "BEARISH": "هابط", "NEUTRAL": "محايد" };
const T_STR    = { "STRONG": "قوي", "MEDIUM": "متوسط", "WEAK": "ضعيف" };
const T_DIR    = { "bullish": "صاعد", "bearish": "هابط" };

function tr(map, key, fallback) { return map[key] != null ? map[key] : (fallback != null ? fallback : key); }


// ── الترخيص ──────────────────────────────────
async function activateLicense() {
  const key = document.getElementById("licenseKey").value.trim();
  const msg = document.getElementById("message");
  if (!key) { msg.textContent = "الرجاء إدخال مفتاح الترخيص"; msg.className = "msg-err"; return; }
  msg.textContent = "جارٍ التحقق..."; msg.className = "";
  try {
    const r = await fetch("/activate", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({licenseKey: key})
    });
    const d = await r.json();
    if (d.success) {
      msg.textContent = "✓ تم تفعيل الترخيص بنجاح"; msg.className = "msg-ok";
      setTimeout(() => window.location.href = "/dashboard", 900);
    } else {
      msg.textContent = "✕ مفتاح ترخيص غير صحيح"; msg.className = "msg-err";
    }
  } catch(e) {
    msg.textContent = "خطأ في الاتصال"; msg.className = "msg-err";
  }
}


// ── تحليل السوق ───────────────────────────────
async function analyzeMarket() {
  const sel    = document.getElementById("pairSelect");
  const tv_sym = sel.value;
  const api_pair = sel.options[sel.selectedIndex]?.dataset?.api || tv_sym.replace("FX:","").replace("FX_IDC:","");
  const candles  = document.getElementById("candleCount").value;
  const btn      = document.getElementById("analyzeBtn");

  btn.classList.add("loading");
  setSignalState("جاري التحليل", "loading");

  try {
    const r = await fetch("/analyze", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({pair: api_pair, candles: parseInt(candles)})
    });
    const d = await r.json();

    if (d.error) {
      setSignalState("خطأ", "wait");
      console.error(d.error);
      return;
    }

    updateSignalPanel(d);
    updateStructurePanel(d);
    updateLiquidityPanel(d);
    updateSmartMoneyPanel(d);
    updateReasons(d.reasons || []);

    if (d.alert && (d.signal === "CALL" || d.signal === "PUT")) {
      playAlert();
      showToast(d);
    }

  } catch(e) {
    setSignalState("خطأ", "wait");
    console.error(e);
  } finally {
    btn.classList.remove("loading");
  }
}


// ── لوحة الإشارة ─────────────────────────────
function setSignalState(text, cls) {
  const el = document.getElementById("signalDirection");
  el.textContent = text;
  el.className = "signal-direction " + (cls || "");
}

function updateSignalPanel(d) {
  const dir = document.getElementById("signalDirection");
  dir.textContent = tr(T_SIGNAL, d.signal, "بالانتظار");
  dir.className   = "signal-direction";
  if (d.signal === "CALL")     dir.classList.add("call");
  else if (d.signal === "PUT") dir.classList.add("put");
  else                         dir.classList.add("wait");

  setText("signalPair",       d.pair || "—");
  setText("signalConfidence", d.confidence + "%");
  setText("signalEntry",      d.entry_price || "—");
  setText("signalExpiry",     d.expiry || "—");
  setText("signalRisk",       tr(T_RISK, d.risk, "—"));
  setText("signalEntryType",  d.entry_type || "—");

  const fill = document.getElementById("confFill");
  if (fill) {
    setTimeout(() => fill.style.width = Math.min(d.confidence, 100) + "%", 50);
  }

  // لون المخاطرة
  const riskEl = document.getElementById("signalRisk");
  if (riskEl) {
    riskEl.className = "meta-val";
    if (d.risk === "LOW")    riskEl.style.color = "var(--call)";
    if (d.risk === "MEDIUM") riskEl.style.color = "var(--wait)";
    if (d.risk === "HIGH")   riskEl.style.color = "var(--put)";
  }
}


// ── لوحة الهيكل ──────────────────────────────
function updateStructurePanel(d) {
  setEngVal("eTrend", tr(T_TREND, d.trend, "—"),
    d.trend === "BULLISH" ? "val-bull" : d.trend === "BEARISH" ? "val-bear" : "val-dim");

  setEngVal("eBos", d.bos
    ? ("كسر " + tr(T_DIR, d.bos_direction, "")) : "لا يوجد كسر",
    d.bos ? (d.bos_direction === "bullish" ? "val-bull" : "val-bear") : "val-dim");

  setEngVal("eChoch", d.choch ? "⚠ موجود" : "سليم",
    d.choch ? "val-warn" : "val-bull");

  setEngVal("eStrength", tr(T_STR, d.market_strength, "—") + (d.strength_pct ? ` (${d.strength_pct}%)` : ""),
    d.market_strength === "STRONG" ? "val-bull" : d.market_strength === "WEAK" ? "val-bear" : "val-gold");

  setEngVal("eHHHL", `HH×${d.hh||0}  HL×${d.hl||0}`, "val-bull");
  setEngVal("eLLLH", `LL×${d.ll||0}  LH×${d.lh||0}`, "val-bear");
}


// ── لوحة السيولة ─────────────────────────────
function updateLiquidityPanel(d) {
  const sw = d.liquidity_sweep;
  if (sw) {
    setEngVal("eSweep", (sw.description || "كنس سيولة") + ` @ ${sw.level}`, "val-gold");
  } else {
    setEngVal("eSweep", "لا يوجد", "val-dim");
  }

  const sh = d.stop_hunt;
  if (sh && typeof sh === "object") {
    setEngVal("eStopHunt", sh.description || tr(T_DIR, sh.direction, ""), "val-warn");
  } else {
    setEngVal("eStopHunt", "لا يوجد", "val-dim");
  }

  const fb = d.fake_breakout;
  if (fb && typeof fb === "object") {
    setEngVal("eFakeBO", tr(T_DIR, fb.direction, "نعم"), "val-warn");
  } else {
    setEngVal("eFakeBO", fb ? "نعم" : "لا", fb ? "val-warn" : "val-dim");
  }

  setEngVal("eEqHL", `قمم:${d.equal_highs||0}  قيعان:${d.equal_lows||0}`,
    (d.equal_highs > 2 || d.equal_lows > 2) ? "val-gold" : "val-dim");
}


// ── لوحة المال الذكي ─────────────────────────
function updateSmartMoneyPanel(d) {
  const ic = d.institutional_candle;
  if (ic) {
    const isB = ic.type === "bullish_institutional";
    setEngVal("eInstit",
      `${isB ? "صاعدة" : "هابطة"} · جسم ${ic.body_ratio}%`,
      isB ? "val-bull" : "val-bear");
  } else {
    setEngVal("eInstit", "لا يوجد", "val-dim");
  }

  setEngVal("eBullFVG",    d.total_bullish_fvg  || 0, d.total_bullish_fvg  > 0 ? "val-bull" : "val-dim");
  setEngVal("eBearFVG",    d.total_bearish_fvg  || 0, d.total_bearish_fvg  > 0 ? "val-bear" : "val-dim");
  setEngVal("eBullOB",     d.total_bullish_obs  || 0, d.total_bullish_obs  > 0 ? "val-bull" : "val-dim");
  setEngVal("eBearOB",     d.total_bearish_obs  || 0, d.total_bearish_obs  > 0 ? "val-bear" : "val-dim");
  setEngVal("eBreakers",   d.breaker_blocks     || 0, d.breaker_blocks     > 0 ? "val-gold" : "val-dim");
  setEngVal("eImbalances", d.imbalances         || 0, d.imbalances         > 0 ? "val-gold" : "val-dim");
  setEngVal("eRound",      d.round_number || "—", "val-gold");
}


// ── الأسباب ──────────────────────────────────
function updateReasons(reasons) {
  const ul = document.getElementById("reasonsList");
  if (!ul) return;
  if (!reasons || !reasons.length) {
    ul.innerHTML = '<li class="reason-placeholder">لا توجد شروط مفعّلة</li>';
    return;
  }
  ul.innerHTML = reasons.map(r => {
    const isWarn = r.includes("⚠") || r.toLowerCase().includes("choch");
    return `<li class="reason-item${isWarn ? " reason-warn" : ""}">${escHtml(r)}</li>`;
  }).join("");
}


// ── الإشعار المنبثق ──────────────────────────
function showToast(d) {
  const toast = document.getElementById("signalToast");
  const dir   = document.getElementById("toastDir");
  const det   = document.getElementById("toastDetails");
  if (!toast) return;
  dir.textContent = tr(T_SIGNAL, d.signal, d.signal);
  dir.className   = "toast-dir " + (d.signal === "CALL" ? "call" : "put");
  det.innerHTML   = `${d.pair}  |  دخول: ${d.entry_price}<br>الثقة: ${d.confidence}%  |  انتهاء: ${d.expiry}`;
  toast.classList.add("visible");
  setTimeout(() => toast.classList.remove("visible"), 5000);
}


// ── الصوت ─────────────────────────────────────
function playAlert() {
  const s = document.getElementById("entrySound");
  if (s) { s.currentTime = 0; s.play().catch(() => {}); }
}


// ── أدوات مساعدة ─────────────────────────────
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function setEngVal(id, val, cls) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = val;
  el.className = "eng-val " + (cls || "");
}

function escHtml(s) {
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
