"""
Taiwan Market Data Fetcher
--------------------------
Fetches ALL listed stocks and ETFs from TWSE/TPEX open APIs in one shot.
No static ticker list needed — the API returns the entire market.

Primary: TWSE/TPEX Open Data APIs (1 request = all stocks)
Fallback: yfinance batch download with expanded static list

Usage:
    stocks, etfs = fetch_tw_market_movers(top_n=25)
"""

import json
import sys
import requests
import datetime as dt
from zoneinfo import ZoneInfo

# ─── Core stocks that ALWAYS appear regardless of daily movement ───
CORE_STOCKS = {"2330", "2317", "2454", "2308", "2382"}
CORE_ETFS   = {"0050", "0056", "00878"}

# ─── Sector mapping for common stocks ───
SECTOR_MAP = {
    "1101": "水泥", "1102": "亞泥", "1216": "食品", "1301": "塑化", "1303": "塑化",
    "1326": "塑化", "2002": "鋼鐵", "2105": "紡織", "2207": "汽車", "2301": "光電",
    "2303": "晶圓代工", "2308": "電源/AI", "2317": "AI 伺服器", "2327": "IC 設計",
    "2330": "半導體", "2344": "記憶體", "2345": "網通", "2353": "電子", "2357": "電子",
    "2376": "AI 伺服器", "2377": "NB代工", "2379": "IC 設計", "2382": "伺服器",
    "2395": "映泰", "2412": "電信", "2454": "IC 設計", "2603": "航運", "2609": "航運",
    "2615": "航運", "2618": "航空", "2801": "金融", "2880": "金融", "2881": "金融",
    "2882": "金融", "2883": "金融", "2884": "金融", "2886": "金融", "2887": "金融",
    "2890": "金融", "2891": "金融", "2892": "金融", "2912": "通路", "3008": "光學",
    "3034": "IC 設計", "3036": "IC 通路", "3037": "網通", "3231": "伺服器",
    "3443": "封測", "3481": "面板", "3529": "精密機械", "3661": "IC 設計",
    "3711": "封測", "4904": "電信", "4938": "代工", "5871": "金融", "5876": "金融",
    "5880": "金融", "6505": "塑化", "6669": "光學", "6770": "晶圓代工",
    "8046": "PCB", "8454": "網通",
}

ETF_CATEGORY_MAP = {
    "0050": "大盤", "0051": "中型100", "0052": "科技",  "0055": "金融",
    "0056": "高股息", "006201": "富邦上證", "006203": "富邦印度",
    "006205": "富邦日本", "006206": "富邦歐洲", "006208": "大盤",
    "00631L": "槓桿", "00632R": "反向", "00635U": "黃金",
    "00646": "美股", "00662": "美股科技", "00670L": "美股槓桿",
    "00679B": "美債", "00687B": "美債", "00690": "兆豐藍籌30",
    "00692": "治理", "00701": "高股息", "00713": "低波動",
    "00733": "中小型", "00757": "美科技", "00770": "美股科技",
    "00830": "美股半導體", "00850": "ESG", "00876": "全球科技",
    "00878": "ESG 高息", "00881": "5G", "00885": "越南",
    "00888": "ESG", "00891": "半導體", "00892": "半導體",
    "00893": "電動車", "00895": "電動車", "00896": "中信綠能",
    "00900": "高股息", "00905": "小資高息", "00912": "智能選股",
    "00913": "晶圓製造", "00915": "存股", "00918": "永豐存債",
    "00919": "高股息", "00921": "兆豐龍頭", "00922": "國泰台灣領袖",
    "00923": "群益台ESG", "00927": "群益半導體收益",
    "00929": "科技+息", "00930": "永豐優息存股",
    "00934": "中信半導體", "00935": "科技", "00936": "台新臺灣永續",
    "00937B": "群益長天期", "00939": "統一台灣高息精選",
    "00940": "價值+息", "00941B": "中信投信長天期",
    "00943": "兆豐台灣ESG", "00944": "野村趨勢動能",
    "00946": "群益台灣半導體收益",
}

# ─── TWSE Open API ───

def fetch_twse_all():
    """
    Fetch ALL TWSE-listed securities' daily data in one API call.
    Returns a list of dicts with: code, name, close, change, change_pct, volume
    """
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    try:
        resp = requests.get(url, timeout=30, headers={"Accept": "application/json"})
        resp.raise_for_status()
        raw = resp.json()
        results = []
        for row in raw:
            try:
                code = row.get("Code", "").strip()
                name = row.get("Name", "").strip()
                close_str = row.get("ClosingPrice", "").replace(",", "")
                open_str  = row.get("OpeningPrice", "").replace(",", "")
                if not code or not close_str or close_str == "--":
                    continue
                close_price = float(close_str)
                # Change calculation: ClosingPrice vs OpeningPrice as proxy
                # TWSE also provides "Change" field directly
                change_str = row.get("Change", "").replace(",", "")
                if change_str and change_str != "--":
                    change = float(change_str)
                elif open_str and open_str != "--":
                    change = close_price - float(open_str)
                else:
                    change = 0.0

                # Calculate previous close from change
                prev_close = close_price - change
                change_pct = (change / prev_close * 100) if prev_close != 0 else 0.0

                vol_str = row.get("TradeVolume", "0").replace(",", "")
                volume = int(vol_str) if vol_str else 0

                results.append({
                    "code": code,
                    "name": name,
                    "price": close_price,
                    "change": change,
                    "change_pct": round(change_pct, 2),
                    "volume": volume,
                })
            except (ValueError, TypeError):
                continue
        print(f"  TWSE API: fetched {len(results)} securities")
        return results
    except Exception as e:
        print(f"  [warn] TWSE API failed: {e}", file=sys.stderr)
        return []


def fetch_tpex_all():
    """
    Fetch ALL TPEX (OTC) securities' daily data.
    """
    # TPEX uses a different API format
    today = dt.datetime.now(ZoneInfo("Asia/Taipei"))
    # TPEX date format: 民國年/月/日
    roc_year = today.year - 1911
    date_str = f"{roc_year}/{today.month:02d}/{today.day:02d}"

    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    params = {"l": "zh-tw", "d": date_str, "o": "json"}
    try:
        resp = requests.get(url, timeout=30, params=params)
        resp.raise_for_status()
        raw = resp.json()
        results = []
        data_rows = raw.get("aaData", [])
        for row in data_rows:
            try:
                if len(row) < 9:
                    continue
                code = str(row[0]).strip()
                name = str(row[1]).strip()
                close_str = str(row[2]).replace(",", "")
                change_str = str(row[3]).replace(",", "")
                if not code or close_str == "--" or not close_str:
                    continue
                close_price = float(close_str)
                change = float(change_str) if change_str and change_str != "--" else 0.0
                prev_close = close_price - change
                change_pct = (change / prev_close * 100) if prev_close != 0 else 0.0
                vol_str = str(row[8]).replace(",", "") if len(row) > 8 else "0"
                volume = int(vol_str) if vol_str else 0

                results.append({
                    "code": code,
                    "name": name,
                    "price": close_price,
                    "change": change,
                    "change_pct": round(change_pct, 2),
                    "volume": volume,
                })
            except (ValueError, TypeError):
                continue
        print(f"  TPEX API: fetched {len(results)} securities")
        return results
    except Exception as e:
        print(f"  [warn] TPEX API failed: {e}", file=sys.stderr)
        return []


# ─── Classify into stocks vs ETFs ───

def is_etf_code(code):
    """Determine if a TWSE/TPEX code is an ETF."""
    # Taiwan ETFs: 0050-0059, 006xxx, 00xxx, etc.
    # Generally: starts with "00" and is 4-6 chars, or starts with "0" and is 4 chars
    if code.startswith("00"):
        return True
    if len(code) == 4 and code.startswith("0") and code[1:].isdigit():
        return True
    return False


def classify_and_enrich(all_data):
    """
    Split securities into stocks and ETFs, add sector/category labels.
    """
    stocks = []
    etfs = []

    for item in all_data:
        code = item["code"]

        if is_etf_code(code):
            item["category"] = ETF_CATEGORY_MAP.get(code, "其他")
            item["core"] = code in CORE_ETFS
            etfs.append(item)
        else:
            # Only include regular stocks (4-digit numeric codes)
            if len(code) == 4 and code.isdigit():
                item["sector"] = SECTOR_MAP.get(code, guess_sector(item["name"]))
                item["core"] = code in CORE_STOCKS
                stocks.append(item)

    return stocks, etfs


def guess_sector(name):
    """Rough sector guess from stock name (fallback)."""
    if any(k in name for k in ["金", "銀行", "壽", "證券"]):
        return "金融"
    if any(k in name for k in ["電", "科技", "半導", "光"]):
        return "電子"
    if any(k in name for k in ["鋼", "鐵"]):
        return "鋼鐵"
    if any(k in name for k in ["航", "運"]):
        return "航運"
    if any(k in name for k in ["建", "營造"]):
        return "營建"
    if any(k in name for k in ["食", "飲"]):
        return "食品"
    return "其他"


# ─── Main entry point ───

def pick_top(items, n, core_set):
    """
    Pick top n items:
    1. Core items always included.
    2. Fill remaining slots with biggest absolute movers.
    3. Sort by change_pct descending (winners first).
    """
    core = [i for i in items if i.get("core")]
    rest = [i for i in items if not i.get("core")]
    rest.sort(key=lambda x: abs(x.get("change_pct", 0)), reverse=True)
    picked = core + rest[: max(0, n - len(core))]
    picked.sort(key=lambda x: x.get("change_pct", 0), reverse=True)
    return picked[:n]


def fetch_tw_market(top_stocks=25, top_etfs=25):
    """
    Main entry: fetch full Taiwan market data and return top movers.
    Returns: (top_stocks_list, top_etfs_list, taiex_data)
    """
    print("  Fetching TWSE (all listed securities) ...")
    twse_data = fetch_twse_all()

    print("  Fetching TPEX (all OTC securities) ...")
    tpex_data = fetch_tpex_all()

    all_data = twse_data + tpex_data
    total = len(all_data)
    print(f"  Total securities fetched: {total}")

    if total == 0:
        print("  [warn] No data from TWSE/TPEX APIs. Will need yfinance fallback.")
        return [], [], None

    stocks, etfs = classify_and_enrich(all_data)
    print(f"  Classified: {len(stocks)} stocks, {len(etfs)} ETFs")

    # Find TAIEX from the data (code = "IX0001" or similar) or fetch separately
    # TWSE STOCK_DAY_ALL doesn't include the index itself
    taiex = None  # Will be fetched separately via yfinance

    top_s = pick_top(stocks, top_stocks, CORE_STOCKS)
    top_e = pick_top(etfs,   top_etfs,   CORE_ETFS)

    # Convert to the format expected by the report template
    for item in top_s + top_e:
        item["ticker"] = item["code"] + ".TW"  # yfinance format

    return top_s, top_e, taiex


# ─── yfinance fallback (when TWSE/TPEX APIs fail) ───

def fetch_tw_yfinance_fallback(ticker_list, n=25):
    """
    Batch-download via yfinance as fallback.
    ticker_list should be a list of dicts with 'ticker', 'name', 'sector'/'category', 'core'.
    """
    import yfinance as yf

    tickers_str = [item["ticker"] for item in ticker_list]
    try:
        data = yf.download(tickers_str, period="5d", group_by="ticker", progress=False)
        results = []
        for item in ticker_list:
            tk = item["ticker"]
            try:
                if tk in data.columns.get_level_values(0):
                    closes = data[tk]["Close"].dropna()
                    if len(closes) >= 2:
                        latest = float(closes.iloc[-1])
                        prev = float(closes.iloc[-2])
                        change = latest - prev
                        change_pct = (change / prev * 100) if prev else 0
                        results.append({
                            **item,
                            "code": tk.replace(".TW", "").replace(".TWO", ""),
                            "price": latest,
                            "change": change,
                            "change_pct": round(change_pct, 2),
                        })
            except Exception:
                continue
        return pick_top(results, n, CORE_STOCKS | CORE_ETFS)
    except Exception as e:
        print(f"  [error] yfinance batch failed: {e}", file=sys.stderr)
        return []


if __name__ == "__main__":
    """Quick test: run this file directly to see what the APIs return."""
    stocks, etfs, _ = fetch_tw_market(top_stocks=10, top_etfs=10)
    print(f"\n=== Top 10 Stocks ===")
    for s in stocks:
        print(f"  {s['code']} {s['name']:10s}  {s['change_pct']:+.2f}%  {s.get('sector','')}")
    print(f"\n=== Top 10 ETFs ===")
    for e in etfs:
        print(f"  {e['code']} {e['name']:20s}  {e['change_pct']:+.2f}%  {e.get('category','')}")
