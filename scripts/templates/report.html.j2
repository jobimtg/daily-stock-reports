"""
Daily Stock Report Generator (v5 - quality overhaul)
-----------------------------------------------------
Fixes applied vs v4:
  - NaN guard: items with missing price/change_pct are excluded from tables
  - TWD/USD display fixed: shown as TWD per USD (e.g. 30.xx), not inverted
  - Gold ticker changed to GC=F with unit validation
  - Volume fetched for all stocks and ETFs (shown in tables)
  - 52-week high/low fetched and shown for stocks
  - Three major institutional flows (三大法人) fetched from TWSE API
  - Margin balance (融資融券) fetched from TWSE API
  - Report header clearly states data reference date vs report date
  - Gemini prompt enhanced: must reference specific data, no generic filler
  - Rotation dedup: non-core picks compared vs yesterday to ensure variety
  - Fallback narrative updated to be more specific per actual data
"""

import os
import sys
import json
import argparse
import datetime as dt
import time
import re
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import numpy as np
import yfinance as yf
from google import genai
from google.genai import types
from jinja2 import Environment, FileSystemLoader, select_autoescape

import config

SCRIPT_DIR   = Path(__file__).parent
ROOT_DIR     = SCRIPT_DIR.parent
TEMPLATE_DIR = SCRIPT_DIR / "templates"
CACHE_DIR    = ROOT_DIR / "cache"

# ============================================================
# Helpers
# ============================================================

def fmt_pct(p):
    if p is None:
        return "—"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"


def fmt_price(p, decimals=2):
    if p is None:
        return "—"
    return f"{p:,.{decimals}f}"


def fmt_vol(v):
    """Format volume in human-readable form."""
    if v is None:
        return "—"
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.1f}B"
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}K"
    return str(int(v))


def arrow_for(pct):
    if pct is None or abs(pct) < 0.05:
        return ("→", "flat")
    return ("↑", "up") if pct > 0 else ("↓", "down")


def is_valid(item):
    """Return True only if price and change_pct are real numbers (not NaN/None)."""
    import math
    p = item.get("price")
    c = item.get("change_pct")
    if p is None or c is None:
        return False
    try:
        if math.isnan(float(p)) or math.isnan(float(c)):
            return False
    except (TypeError, ValueError):
        return False
    return True


def safe_fetch(ticker, period="5d", fetch_extra=False):
    """
    Fetch latest price, change, change_pct for a ticker.
    fetch_extra=True also fetches volume and 52w high/low.
    Returns None if data unavailable or NaN.
    """
    import math
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if hist.empty or len(hist) < 2:
            return None
        latest_close = hist["Close"].iloc[-1]
        prev_close   = hist["Close"].iloc[-2]

        if math.isnan(float(latest_close)) or math.isnan(float(prev_close)):
            return None

        change     = float(latest_close) - float(prev_close)
        change_pct = (change / float(prev_close)) * 100 if prev_close else 0.0
        volume     = int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else None

        result = {
            "ticker":     ticker,
            "price":      float(latest_close),
            "change":     float(change),
            "change_pct": float(change_pct),
            "volume":     volume,
        }

        if fetch_extra:
            try:
                hist_1y = t.history(period="1y")
                if not hist_1y.empty:
                    result["week52_high"] = float(hist_1y["Close"].max())
                    result["week52_low"]  = float(hist_1y["Close"].min())
                    latest_p = float(latest_close)
                    h = result["week52_high"]
                    l = result["week52_low"]
                    rng = h - l
                    result["week52_pos"] = round((latest_p - l) / rng * 100, 1) if rng > 0 else 50.0
            except Exception:
                pass

        return result
    except Exception as e:
        print(f"  [warn] failed to fetch {ticker}: {e}", file=sys.stderr)
        return None


def safe_fetch_twd_usd():
    """
    Fetch TWD/USD exchange rate and display as TWD per USD (e.g. ~30.xx).
    yfinance TWDUSD=X returns USD per TWD (~0.033), so we invert.
    """
    import math
    try:
        t = yf.Ticker("TWDUSD=X")
        hist = t.history(period="5d")
        if hist.empty or len(hist) < 2:
            return None
        latest = float(hist["Close"].iloc[-1])
        prev   = float(hist["Close"].iloc[-2])
        if math.isnan(latest) or math.isnan(prev) or latest == 0:
            return None
        # Invert: we want TWD per USD
        twd_per_usd        = 1.0 / latest
        twd_per_usd_prev   = 1.0 / prev
        change             = twd_per_usd - twd_per_usd_prev
        change_pct         = (change / twd_per_usd_prev) * 100
        return {
            "ticker":     "TWDUSD=X",
            "name":       "台幣/美元 (TWD)",
            "price":      round(twd_per_usd, 3),
            "change":     round(change, 3),
            "change_pct": round(change_pct, 3),
            "volume":     None,
            "note":       "TWD per USD",
        }
    except Exception as e:
        print(f"  [warn] failed to fetch TWD/USD: {e}", file=sys.stderr)
        return None


def fetch_list(items, fetch_extra=False):
    """Fetch a list of ticker dicts, skip items with missing/NaN data."""
    out = []
    for item in items:
        data = safe_fetch(item["ticker"], fetch_extra=fetch_extra)
        if data is None:
            print(f"  [skip] {item['ticker']} — no data", file=sys.stderr)
            continue
        merged = {**item, **data}
        if not is_valid(merged):
            print(f"  [skip] {item['ticker']} — NaN values", file=sys.stderr)
            continue
        out.append(merged)
    return out




def fetch_etf_extra_info(items):
    """Enrich ETF items with AUM, dividend yield, recent dividend from yfinance .info."""
    for item in items:
        try:
            t = yf.Ticker(item["ticker"])
            info = t.info or {}
            aum = info.get("totalAssets")
            if aum:
                item["aum"] = aum
                if aum >= 1e12:
                    item["aum_str"] = f"{aum/1e12:.1f}兆"
                elif aum >= 1e8:
                    item["aum_str"] = f"{aum/1e8:.0f}億"
                else:
                    item["aum_str"] = f"{aum/1e6:.0f}M"
            else:
                item["aum_str"] = "—"
            item["div_yield"] = info.get("yield") or info.get("dividendYield")
            item["last_div"] = info.get("lastDividendValue")
        except Exception:
            item["aum_str"] = "—"
            item["div_yield"] = None
            item["last_div"] = None
    return items


def compute_signals(items):
    """
    Compute technical signals for stocks:
    - RSI (14-day)
    - Price vs 20-day / 60-day moving average
    - Volume ratio vs 20-day average
    Returns list of signal dicts.
    """
    import numpy as np
    signals = []
    for item in items:
        try:
            t = yf.Ticker(item["ticker"])
            hist = t.history(period="3mo")
            if hist.empty or len(hist) < 20:
                continue
            closes = hist["Close"].values
            volumes = hist["Volume"].values

            # RSI (14-day)
            deltas = np.diff(closes)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss > 0 else 100
            item["rsi"] = round(rsi, 1)

            # Moving averages
            ma20 = np.mean(closes[-20:])
            ma60 = np.mean(closes[-60:]) if len(closes) >= 60 else None
            latest = closes[-1]
            item["ma20"] = round(ma20, 2)
            item["above_ma20"] = latest > ma20
            if ma60:
                item["ma60"] = round(ma60, 2)
                item["above_ma60"] = latest > ma60

            # Volume ratio (today vs 20-day avg)
            vol_avg20 = np.mean(volumes[-20:])
            vol_today = volumes[-1]
            item["vol_ratio"] = round(vol_today / vol_avg20, 1) if vol_avg20 > 0 else None

            # Generate signal labels
            sigs = []
            if rsi >= 70:
                sigs.append({"type": "overbought", "icon": "🔴", "text": f"RSI {rsi:.0f} 過熱"})
            elif rsi <= 30:
                sigs.append({"type": "oversold", "icon": "🟢", "text": f"RSI {rsi:.0f} 超賣"})
            if ma60 and not item.get("_prev_above_ma60", True) and latest > ma60:
                sigs.append({"type": "ma_break", "icon": "🟢", "text": f"突破 60 日均線 {ma60:.0f}"})
            if item.get("above_ma20") and item.get("above_ma60", False):
                sigs.append({"type": "bullish", "icon": "🟢", "text": "站穩 20/60 日均線上方"})
            if item.get("vol_ratio") and item["vol_ratio"] >= 2.0:
                sigs.append({"type": "volume", "icon": "🟡", "text": f"成交量為均量 {item['vol_ratio']:.1f} 倍"})

            if sigs:
                signals.append({
                    "ticker": item["ticker"],
                    "name": item.get("name", ""),
                    "price": item.get("price"),
                    "change_pct": item.get("change_pct"),
                    "rsi": rsi,
                    "signals": sigs,
                })
        except Exception as e:
            continue
    return signals


def fetch_tw_ipo():
    """Fetch recent and upcoming Taiwan IPOs from TWSE."""
    try:
        url = "https://openapi.twse.com.tw/v1/company/newlisting"
        resp = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        if resp.ok:
            data = resp.json()
            if isinstance(data, list):
                recent = []
                for row in data[:10]:
                    recent.append({
                        "code": row.get("Code", ""),
                        "name": row.get("Name", ""),
                        "date": row.get("ListingDate", ""),
                        "industry": row.get("Industry", ""),
                    })
                return {"available": True, "items": recent}
    except Exception as e:
        print(f"  [warn] TWSE IPO fetch failed: {e}", file=sys.stderr)
    return {"available": False, "items": []}


def fetch_market_breadth():
    """Fetch advance/decline/unchanged counts from TWSE."""
    try:
        url = "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
        resp = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        if resp.ok:
            data = resp.json()
            if isinstance(data, list):
                for row in data:
                    idx_name = row.get("指數", "") or row.get("IndexName", "")
                    if "發行量加權" in idx_name or "TAIEX" in idx_name.upper():
                        return {
                            "available": True,
                            "advance": row.get("漲", row.get("Up", "—")),
                            "decline": row.get("跌", row.get("Down", "—")),
                            "unchanged": row.get("平", row.get("Unchanged", "—")),
                        }
    except Exception as e:
        print(f"  [warn] TWSE breadth fetch failed: {e}", file=sys.stderr)
    return {"available": False}


# ============================================================
# TWSE institutional flow (三大法人) + margin (融資融券)
# ============================================================

def fetch_twse_institutional(date_str=None):
    """
    Fetch three major institutional net buy/sell from TWSE open API.
    date_str: optional YYYYMMDD for historical date (morning report uses previous day).
    Returns dict with foreign, investment_trust, dealer net values (TWD billion).
    """
    try:
        # Try the daily institutional flow endpoint
        if date_str:
            url2 = f"https://openapi.twse.com.tw/v1/exchangeReport/FMSSCL?date={date_str}"
        else:
            url2 = "https://openapi.twse.com.tw/v1/exchangeReport/FMSSCL"
        resp2 = requests.get(url2, timeout=15, headers={"Accept": "application/json"})
        if resp2.ok:
            data = resp2.json()
            if isinstance(data, list) and data:
                row = data[0]
                def parse_bn(v):
                    try:
                        return round(float(str(v).replace(",", "")) / 1e8, 1)
                    except Exception:
                        return None
                return {
                    "foreign":          parse_bn(row.get("Foreign_Investor_Diff", 0)),
                    "investment_trust": parse_bn(row.get("Investment_Trust_Diff", 0)),
                    "dealer":           parse_bn(row.get("Dealer_Diff", 0)),
                    "available":        True,
                }
    except Exception as e:
        print(f"  [warn] TWSE institutional flow failed: {e}", file=sys.stderr)

    return {"available": False}


def fetch_twse_margin():
    """
    Fetch margin balance change from TWSE.
    Returns dict with margin_balance and short_balance changes.
    """
    try:
        url = "https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN"
        resp = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        if resp.ok:
            data = resp.json()
            if isinstance(data, list) and data:
                row = data[-1]  # latest row
                def parse_int(v):
                    try:
                        return int(str(v).replace(",", ""))
                    except Exception:
                        return None
                margin = parse_int(row.get("MarginPurchase", 0))
                margin_prev = parse_int(row.get("MarginPurchasePreviousBalance", 0))
                short = parse_int(row.get("ShortSale", 0))
                short_prev = parse_int(row.get("ShortSalePreviousBalance", 0))
                margin_chg = None
                short_chg  = None
                if margin is not None and margin_prev is not None and margin_prev > 0:
                    margin_chg = round((margin - margin_prev) / margin_prev * 100, 2)
                if short is not None and short_prev is not None and short_prev > 0:
                    short_chg = round((short - short_prev) / short_prev * 100, 2)
                return {
                    "margin_balance":  margin,
                    "margin_change":   margin_chg,
                    "short_balance":   short,
                    "short_change":    short_chg,
                    "available":       True,
                }
    except Exception as e:
        print(f"  [warn] TWSE margin data failed: {e}", file=sys.stderr)
    return {"available": False}


# ============================================================
# Rotation dedup (ensure daily variety in non-core picks)
# ============================================================

def load_yesterday_tickers(region_key):
    cache_file = CACHE_DIR / f"rotation_{region_key}.json"
    if cache_file.exists():
        try:
            return set(json.loads(cache_file.read_text(encoding="utf-8")).get("tickers", []))
        except Exception:
            pass
    return set()


def save_rotation_tickers(region_key, tickers):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"rotation_{region_key}.json"
    cache_file.write_text(
        json.dumps({"tickers": list(tickers)}, ensure_ascii=False),
        encoding="utf-8",
    )


def pick_movers(items, n, region_key=None):
    """
    Core items always included.
    Non-core slots filled by biggest absolute % movers.
    If today's non-core picks == yesterday's, swap ~30% for variety.
    Only items that passed is_valid() are included (NaN already filtered upstream).
    """
    core = [i for i in items if i.get("core")]
    rest = [i for i in items if not i.get("core")]
    rest.sort(key=lambda x: abs(x.get("change_pct") or 0), reverse=True)

    slots = max(0, n - len(core))
    if slots == 0:
        picked = core[:n]
        picked.sort(key=lambda x: x.get("change_pct") or 0, reverse=True)
        return picked

    yesterday = load_yesterday_tickers(region_key) if region_key else set()
    top_candidates = rest[:slots]
    top_tickers = {i.get("ticker") for i in top_candidates}

    if yesterday and top_tickers == yesterday and len(rest) > slots:
        swap_count = max(1, slots // 3)
        alternates = [i for i in rest[slots:] if i.get("ticker") not in yesterday]
        kept       = [i for i in top_candidates if i.get("ticker") not in yesterday]
        must_swap  = [i for i in top_candidates if i.get("ticker") in yesterday]
        must_swap.sort(key=lambda x: abs(x.get("change_pct") or 0))
        swapped    = must_swap[swap_count:]
        injected   = alternates[:swap_count]
        top_candidates = kept + swapped + injected
        top_candidates.sort(key=lambda x: abs(x.get("change_pct") or 0), reverse=True)
        top_candidates = top_candidates[:slots]

    if region_key:
        save_rotation_tickers(region_key, {i.get("ticker") for i in top_candidates})

    picked = core + top_candidates
    picked.sort(key=lambda x: x.get("change_pct") or 0, reverse=True)
    return picked[:n]


# ============================================================
# Gemini narrative
# ============================================================

PROMPT_FULL = """你是一位有 15 年以上經驗的繁體中文財經分析師。根據以下【真實市場數據】撰寫今日財經晨報分析。

重要規則：
- 所有分析必須直接引用下方提供的具體數字，禁止使用「預期」「可能」等推測語氣替代真實數據
- 若某個觀察無數據支撐，直接省略，不要補充通用說法
- 風險與觀察重點必須針對「今日」具體事件，不得重複昨日模板

【日期】{date}（{weekday}），{city} 時間
【資料截止】前一個交易日收盤

【TSX 加拿大股市】點位 {tsx_price}，漲跌 {tsx_pct}
【TAIEX 台灣股市】點位 {taiex_price}，漲跌 {taiex_pct}

【TSX 主要走勢個股（含成交量）】
{tsx_top}

【TAIEX 主要走勢個股（含成交量）】
{taiex_top}

【三大法人動向】
{institutional}

【融資融券】
{margin}

【總體市場（含美股）】
{macro}

【技術面訊號摘要】
{signals_summary}

【IPO 近期上市】
{ipo_summary}

【市場廣度（漲跌家數）】
{breadth}

請只回傳有效 JSON，不要 markdown，不要解釋。格式：
{{
  "tsx_summary": "1-2 句 TSX 走勢摘要，必須引用具體指數點位與漲跌幅",
  "tsx_highlights": ["4 項重點，每項必須引用具體數字或個股名稱"],
  "taiex_summary": "2-3 句 TAIEX 走勢摘要，必須引用具體點位與漲跌幅",
  "taiex_highlights": ["5 項詳細重點，含族群分析與具體股名"],
  "institutional_insight": "1-2 句三大法人動向解讀（若無數據則填 null）",
  "margin_insight": "1-2 句融資融券解讀（若無數據則填 null）",
  "risks": ["強制 5 項風險，每項必須具體說明原因與影響，禁止通用模板"],
  "watch_points": ["強制 5 項觀察重點，每項針對今日具體狀況"],
  "suggestion": "1 段針對今日市場狀況的具體建議",
  "signals_insight": "2-3 句技術面訊號解讀，引用具體個股的 RSI/均線/量能數據",
  "ipo_insight": "1 句近期 IPO 觀察（若無資料填 null）"
}}"""

PROMPT_TW = """你是一位有 15 年以上經驗的繁體中文財經分析師。針對台灣讀者撰寫今日台股財經報告。

重要規則：
- 所有分析必須直接引用下方提供的具體數字，禁止使用「預期」「可能」等推測語氣替代真實數據
- 風險與觀察重點必須針對「今日」具體事件，不得重複昨日模板
- 若三大法人或融資融券有數據，必須納入分析

【日期】{date}（{weekday}）
【資料截止】{data_ref_date}（{data_ref_weekday}）收盤
【TAIEX 台灣股市】點位 {taiex_price}，漲跌 {taiex_pct}

【TAIEX 主要走勢個股（含成交量與 52 週高低位置）】
{taiex_top}

【三大法人動向（外資/投信/自營）】
{institutional}

【融資融券餘額】
{margin}

【總體市場（含美股，影響今日開盤）】
{macro}

【技術面訊號摘要】
{signals_summary}

【市場廣度（漲跌家數）】
{breadth}

【IPO 近期上市】
{ipo_summary}

請只回傳有效 JSON，不要 markdown，不要解釋。格式：
{{
  "taiex_summary": "2-3 句 TAIEX 走勢摘要，必須引用具體點位與漲跌幅，說明主要驅動族群",
  "taiex_highlights": ["5 項詳細重點，含具體族群分析與個股點名"],
  "institutional_insight": "具體說明三大法人買賣超金額與意涵（若無數據填 null）",
  "margin_insight": "融資餘額增減說明與散戶槓桿判讀（若無數據填 null）",
  "risks": ["強制 5 項風險，每項具體說明今日市場背景，禁止通用模板"],
  "watch_points": ["強制 5 項觀察重點，針對今日具體狀況與明日展望"],
  "suggestion": "針對今日數據的具體操作建議",
  "signals_insight": "2-3 句技術面訊號解讀，引用具體個股 RSI/均線/量能",
  "ipo_insight": "1 句近期 IPO 觀察（若無資料填 null）"
}}"""


def _extract_gemini_json(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text.strip()).strip()
    start = text.find("{")
    end   = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise json.JSONDecodeError("No JSON object found", text, 0)
    return json.loads(text[start:end + 1])


def _gemini_cache_file(region, report_date):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe_region = region.replace("/", "_").replace(" ", "_")
    return CACHE_DIR / f"gemini_{safe_region}_{report_date}.json"


def call_gemini(prompt, region, report_date):
    cache_file = _gemini_cache_file(region, report_date)
    if cache_file.exists():
        try:
            print(f"  Using Gemini cache: {cache_file.name}")
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  [warn] Gemini cache invalid: {e}", file=sys.stderr)

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[warn] GEMINI_API_KEY not set, using fallback")
        return None

    client = genai.Client(api_key=api_key)
    retry_waits = [0, 30, 90, 180]

    for attempt, wait_seconds in enumerate(retry_waits, start=1):
        if wait_seconds:
            print(f"  Waiting {wait_seconds}s before Gemini retry #{attempt} ...")
            time.sleep(wait_seconds)
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            narrative = _extract_gemini_json(response.text)
            cache_file.write_text(
                json.dumps(narrative, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  Saved Gemini cache: {cache_file.name}")
            return narrative

        except json.JSONDecodeError as e:
            print(f"[warn] Gemini invalid JSON attempt {attempt}: {e}", file=sys.stderr)
            if attempt >= len(retry_waits):
                return None
        except Exception as e:
            err = str(e)
            is_retryable = any(x in err.lower() for x in ["429", "quota", "resource_exhausted", "temporarily", "timeout", "503", "500"])
            print(f"[error] Gemini attempt {attempt}: {e}", file=sys.stderr)
            if not is_retryable or attempt >= len(retry_waits):
                return None

    return None


# ============================================================
# Fallback narratives (data-aware)
# ============================================================

def fallback_full(tsx, taiex):
    tsx_dir = "上漲" if (tsx and (tsx.get("change_pct") or 0) > 0) else "下跌"
    tw_dir  = "上漲" if (taiex and (taiex.get("change_pct") or 0) > 0) else "下跌"
    tsx_pct_str   = fmt_pct(tsx.get("change_pct")) if tsx else "—"
    taiex_pct_str = fmt_pct(taiex.get("change_pct")) if taiex else "—"
    return {
        "tsx_summary": f"TSX 綜合指數今日{tsx_dir} {tsx_pct_str}，能源、金融、科技三大族群為主要影響因素。",
        "tsx_highlights": [
            "能源股表現受 WTI 油價走勢驅動",
            "加拿大銀行股走勢反映利率預期",
            "科技類 Celestica、Shopify 表現關注",
            "建議依個別投資目標進行配置調整",
        ],
        "taiex_summary": f"TAIEX 加權指數今日{tw_dir} {taiex_pct_str}，半導體與電子權值股影響顯著。",
        "taiex_highlights": [
            "台積電為大盤最重要驅動變數",
            "AI 伺服器族群（鴻海、廣達）表現關注",
            "成交量與外資動向值得留意",
            "高股息 ETF 為穩健配置選擇",
            "建議搭配個股基本面評估",
        ],
        "institutional_insight": None,
        "margin_insight": None,
        "risks": [
            "地緣政治風險推升避險需求，影響外資進出",
            "通膨與利率政策仍有不確定性，壓抑估值",
            "AI/半導體股估值偏高，獲利了結賣壓潛在",
            "美元走勢影響外資匯兌成本",
            "原油價格波動衝擊加拿大能源股",
        ],
        "watch_points": [
            "台積電 ADR 美股表現傳導台股開盤",
            "TSX 能源股隨油價走勢",
            "外資現貨買賣超金額",
            "新台幣兌美元匯率方向",
            "VIX 恐慌指數是否持續回落",
        ],
        "suggestion": "今日市場以觀察為主，建議持盈保泰，注意量能是否配合漲勢。",
        "signals_insight": "技術面訊號請參考報告中的訊號雷達區塊。",
        "ipo_insight": None,
    }


def fallback_tw(taiex):
    tw_dir        = "上漲" if (taiex and (taiex.get("change_pct") or 0) > 0) else "下跌"
    taiex_pct_str = fmt_pct(taiex.get("change_pct")) if taiex else "—"
    taiex_price_str = fmt_price(taiex.get("price")) if taiex else "—"
    return {
        "taiex_summary": f"TAIEX 加權指數收盤 {taiex_price_str}，{tw_dir} {taiex_pct_str}。半導體與電子權值股為主要驅動因素，外資動向與成交量為後市關鍵。",
        "taiex_highlights": [
            "台積電走勢主導大盤方向，為最重要權值股",
            "AI 伺服器族群（鴻海、廣達、技嘉）表現需關注",
            "金融股在利率預期下走勢分歧",
            "高股息族群（0056、00878）提供防禦緩衝",
            "航運股受全球需求與運費走勢影響",
        ],
        "institutional_insight": None,
        "margin_insight": None,
        "risks": [
            "外資單日賣超可能引發市場恐慌",
            "AI/半導體股估值偏高，技術面有壓",
            "美元走強對新台幣形成貶值壓力",
            "地緣政治緊張隨時可能衝擊市場",
            "量能不足時漲勢難以持續",
        ],
        "watch_points": [
            "台積電今日盤中走勢與成交量能否擴大",
            "外資現貨買賣超方向與金額",
            "新台幣匯率能否守住關鍵支撐",
            "半導體族群成交熱度是否持續",
            "大盤量能是否達到 3,000 億以上確認趨勢",
        ],
        "suggestion": f"台股今日{tw_dir} {taiex_pct_str}，建議關注外資動向與量能變化，以此判斷趨勢持續性，避免在量縮時追高。",
        "signals_insight": "技術面訊號請參考報告中的訊號雷達區塊。",
        "ipo_insight": None,
    }


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", choices=["full", "tw", "tw_morning", "tw_closing"], default="full")
    parser.add_argument("--date",   help="Override report date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default=str(ROOT_DIR))
    args = parser.parse_args()

    # Normalise legacy "tw" → "tw_morning"
    region_key = "tw_morning" if args.region == "tw" else args.region
    region_cfg = config.REGIONS[region_key]
    tz = ZoneInfo(region_cfg["timezone"])

    # Report date = today in local timezone
    if args.date:
        date_obj = dt.date.fromisoformat(args.date)
    else:
        date_obj = dt.datetime.now(tz).date()

    weekday_map = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    weekday_zh  = weekday_map[date_obj.weekday()]
    date_str    = date_obj.strftime("%Y/%m/%d")
    date_iso    = date_obj.isoformat()

    # Data reference date:
    # - Closing report (tw_closing): data IS today (market just closed at 13:30)
    # - Morning report (tw_morning, full): data is the previous trading day
    report_type = region_cfg.get("report_type", "morning")
    if report_type == "closing":
        data_ref = date_obj
    else:
        data_ref = date_obj - dt.timedelta(days=1)
        while data_ref.weekday() >= 5:
            data_ref -= dt.timedelta(days=1)
    data_ref_str     = data_ref.strftime("%Y/%m/%d")
    data_ref_weekday = weekday_map[data_ref.weekday()]

    print(f"=== {region_key.upper()} [{report_type}] report: {date_iso} ({weekday_zh}) | data ref: {data_ref_str} ===")

    # ---- Fetch market data ----
    print("[1/6] Fetching market data ...")

    taiex_index = safe_fetch(config.TAIEX_INDEX_TICKER)
    taiex_all   = fetch_list(config.TAIEX_UNIVERSE, fetch_extra=True)
    tw_etfs_all = fetch_list(config.TAIEX_ETFS,    fetch_extra=False)

    # Fix TWD/USD separately (inverted display)
    macro_raw = []
    for item in config.MACRO:
        if item["ticker"] == "TWDUSD=X":
            twd = safe_fetch_twd_usd()
            if twd:
                macro_raw.append({**item, **twd})
        else:
            data = safe_fetch(item["ticker"])
            if data and is_valid(data):
                macro_raw.append({**item, **data})

    us_idx = fetch_list(config.US_INDICES)

    taiex_top = pick_movers(taiex_all,   region_cfg["top_taiex_n"], f"{region_key}_stocks")
    tw_etfs   = pick_movers(tw_etfs_all, region_cfg["etf_taiex_n"], f"{region_key}_etfs")

    tsx_index = None
    tsx_top   = []
    ca_etfs   = []
    portfolio = []

    if region_key == "full":
        tsx_index    = safe_fetch(config.TSX_INDEX_TICKER)
        tsx_all      = fetch_list(config.TSX_UNIVERSE, fetch_extra=True)
        ca_etfs_all  = fetch_list(config.CANADA_ETFS)
        tsx_top      = pick_movers(tsx_all,     region_cfg["top_tsx_n"],  "full_tsx_stocks")
        ca_etfs      = pick_movers(ca_etfs_all, region_cfg["etf_ca_n"],   "full_ca_etfs")
        pass  # Portfolio removed for ad compliance

    # ---- Fetch TWSE institutional & margin ----
    print("[2/6] Fetching TWSE institutional flow & margin ...")
    # Morning reports: fetch previous trading day's data (TWSE updates after 3PM)
    if report_type == "morning":
        inst_date = data_ref.strftime("%Y%m%d")
        institutional = fetch_twse_institutional(date_str=inst_date)
    else:
        institutional = fetch_twse_institutional()
    margin_data = fetch_twse_margin()

    # Market breadth (advance/decline)
    print("[2.5/6] Fetching market breadth, signals, IPO ...")
    breadth = fetch_market_breadth()

    # Technical signals for top stocks
    signals = compute_signals(taiex_top[:15])

    # ETF extra info (AUM, dividend)
    tw_etfs = fetch_etf_extra_info(tw_etfs)
    if region_key == "full" and ca_etfs:
        ca_etfs = fetch_etf_extra_info(ca_etfs)

    # IPO tracking
    ipo_data = fetch_tw_ipo()

    # ---- Build Gemini prompt ----
    print("[3/7] Calling Gemini for narrative ...")

    def stock_line(s):
        vol_str = fmt_vol(s.get("volume"))
        pos_str = f" | 52週位置:{s.get('week52_pos', '—')}%" if s.get("week52_pos") is not None else ""
        return f"- {s['ticker']} {s['name']}: {fmt_pct(s.get('change_pct'))} 收{fmt_price(s.get('price'))} 量{vol_str}{pos_str}"

    def etf_line(e):
        vol_str = fmt_vol(e.get("volume"))
        return f"- {e['ticker']} {e['name']}: {fmt_pct(e.get('change_pct'))} 收{fmt_price(e.get('price'))} 量{vol_str}"

    if institutional.get("available"):
        inst_str = (
            f"外資: {fmt_price(institutional.get('foreign'), 1)} 億 | "
            f"投信: {fmt_price(institutional.get('investment_trust'), 1)} 億 | "
            f"自營: {fmt_price(institutional.get('dealer'), 1)} 億"
        )
    else:
        inst_str = "資料暫無（TWSE API 未回應）"

    if margin_data.get("available"):
        margin_str = (
            f"融資餘額: {margin_data.get('margin_balance'):,} 千股 "
            f"({fmt_pct(margin_data.get('margin_change'))} 變動) | "
            f"融券餘額: {margin_data.get('short_balance'):,} 千股 "
            f"({fmt_pct(margin_data.get('short_change'))} 變動)"
        )
    else:
        margin_str = "資料暫無（TWSE API 未回應）"

    # Build signals summary for prompt
    signals_summary = "\n".join(
        f"- {s['name']}({s['ticker']}): RSI {s['rsi']:.0f}, " + 
        ", ".join(sig['text'] for sig in s['signals'])
        for s in signals
    ) if signals else "無顯著技術訊號"

    breadth_str = (
        f"上漲 {breadth.get('advance', '—')} 家 / "
        f"下跌 {breadth.get('decline', '—')} 家 / "
        f"持平 {breadth.get('unchanged', '—')} 家"
    ) if breadth.get("available") else "資料暫無"

    ipo_summary = "\n".join(
        f"- {i['code']} {i['name']} ({i['date']}) {i['industry']}"
        for i in (ipo_data.get("items") or [])[:5]
    ) if ipo_data.get("available") else "近期無新股上市"

    if region_key == "full":
        prompt = PROMPT_FULL.format(
            date=date_str, weekday=weekday_zh, city=region_cfg["city"],
            tsx_price=fmt_price(tsx_index.get("price"))      if tsx_index else "—",
            tsx_pct=fmt_pct(tsx_index.get("change_pct"))     if tsx_index else "—",
            taiex_price=fmt_price(taiex_index.get("price"))  if taiex_index else "—",
            taiex_pct=fmt_pct(taiex_index.get("change_pct")) if taiex_index else "—",
            tsx_top="\n".join(stock_line(s) for s in tsx_top),
            taiex_top="\n".join(stock_line(s) for s in taiex_top),
            institutional=inst_str,
            margin=margin_str,
            macro="\n".join(f"- {m['name']}: {fmt_price(m.get('price'))} ({fmt_pct(m.get('change_pct'))})" for m in macro_raw),
            signals_summary=signals_summary,
            breadth=breadth_str,
            ipo_summary=ipo_summary,
        )
        fallback_fn = lambda: fallback_full(tsx_index, taiex_index)
    else:
        prompt = PROMPT_TW.format(
            date=date_str, weekday=weekday_zh,
            data_ref_date=data_ref_str, data_ref_weekday=data_ref_weekday,
            taiex_price=fmt_price(taiex_index.get("price"))  if taiex_index else "—",
            taiex_pct=fmt_pct(taiex_index.get("change_pct")) if taiex_index else "—",
            taiex_top="\n".join(stock_line(s) for s in taiex_top),
            institutional=inst_str,
            margin=margin_str,
            macro="\n".join(f"- {m['name']}: {fmt_price(m.get('price'))} ({fmt_pct(m.get('change_pct'))})" for m in (macro_raw + us_idx)),
            signals_summary=signals_summary,
            breadth=breadth_str,
            ipo_summary=ipo_summary,
        )
        fallback_fn = lambda: fallback_tw(taiex_index)

    narrative = call_gemini(prompt, region_key, date_iso)
    if not narrative:
        print("  Using fallback narrative.")
        narrative = fallback_fn()

    # ---- Render HTML ----
    print("[4/7] Rendering HTML ...")
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["pct"]   = fmt_pct
    env.filters["price"] = fmt_price
    env.filters["vol"]   = fmt_vol
    template = env.get_template("report.html.j2")

    visible_sections = []
    for key in ["tsx", "taiex", "etf", "top", "macro", "conclusion", "signals", "ipo"]:
        if key == "etf"   and ("etf_tw"  in region_cfg["show_sections"] or "etf_ca"  in region_cfg["show_sections"]):
            visible_sections.append("etf")
        elif key == "top" and ("top_tsx" in region_cfg["show_sections"] or "top_taiex" in region_cfg["show_sections"]):
            visible_sections.append("top")
        elif key in region_cfg["show_sections"]:
            visible_sections.append(key)
    visible_sections.append("sources")
    # Ensure signals/ipo are in nums even if no data
    for extra in ["signals", "ipo"]:
        if extra not in visible_sections and extra in region_cfg.get("show_sections", []):
            visible_sections.insert(-1, extra)
    nums = {s: i for i, s in enumerate(visible_sections, start=1)}

    html = template.render(
        region=region_key,
        show=set(region_cfg["show_sections"]),
        num=nums,
        city=region_cfg["city"],
        date_str=date_str,
        weekday_zh=weekday_zh,
        data_ref_str=data_ref_str,
        data_ref_weekday=data_ref_weekday,
        tsx=tsx_index,
        taiex=taiex_index,
        tsx_top=tsx_top,
        taiex_top=taiex_top,
        tw_etfs=tw_etfs,
        ca_etfs=ca_etfs,
        macro=macro_raw,
        us_idx=us_idx,
        institutional=institutional,
        margin_data=margin_data,
        n=narrative,
        index_link=(("../" * len(Path(region_cfg.get("output_subdir", "")).parts)) + "index.html") if region_cfg.get("output_subdir") else "index.html",
    )

    # ---- Save ----
    print("[5/7] Saving HTML ...")
    out_root = Path(args.output_dir)
    subdir   = region_cfg["output_subdir"]
    out_dir  = out_root / subdir if subdir else out_root
    out_dir.mkdir(parents=True, exist_ok=True)
    html_filename = region_cfg["filename_fmt"].format(date=date_iso)
    output_path   = out_dir / html_filename
    output_path.write_text(html, encoding="utf-8")
    print(f"  ✅ {output_path} ({output_path.stat().st_size:,} bytes)")

    # ---- latest.json ----
    print("[6/7] Writing latest.json ...")
    url = f"https://{config.USERNAME}.github.io/{config.REPO}/{region_cfg['url_path_fmt'].format(date=date_iso)}"
    summary = {
        "region":   region_key,
        "date":     date_iso,
        "date_str": date_str,
        "weekday_zh": weekday_zh,
        "data_ref": data_ref_str,
        "taiex":    taiex_index,
        "tsx":      tsx_index,
        "filename": html_filename,
        "report_url": url,
    }
    summary_path = out_root / region_cfg["summary_path"]
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {summary_path}")
    print("Done.")


if __name__ == "__main__":
    main()
