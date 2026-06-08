"""
Daily Stock Report Generator (v3 - multi-region)
-------------------------------------------------
Generates two report variants based on --region flag:
  full   → TSX + TAIEX + portfolio + macro (for Jobi)
  tw     → TAIEX-only + macro (for Taiwan family, no portfolio)

Usage:
    python scripts/generate_daily_report.py --region full
    python scripts/generate_daily_report.py --region tw
    python scripts/generate_daily_report.py --region full --date 2026-06-07
"""

import os
import sys
import json
import argparse
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import yfinance as yf
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader, select_autoescape

import config

SCRIPT_DIR   = Path(__file__).parent
ROOT_DIR     = SCRIPT_DIR.parent
TEMPLATE_DIR = SCRIPT_DIR / "templates"

# ============================================================
# Helpers
# ============================================================

def fmt_pct(p):
    if p is None: return "—"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"

def fmt_price(p, decimals=2):
    if p is None: return "—"
    return f"{p:,.{decimals}f}"

def arrow_for(pct):
    if pct is None or abs(pct) < 0.05:
        return ("→", "flat")
    return ("↑", "up") if pct > 0 else ("↓", "down")

def safe_fetch(ticker, period="5d"):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if hist.empty or len(hist) < 2:
            return None
        latest = hist["Close"].iloc[-1]
        prev   = hist["Close"].iloc[-2]
        change = latest - prev
        change_pct = (change / prev) * 100 if prev else 0.0
        return {
            "ticker": ticker, "price": float(latest),
            "change": float(change), "change_pct": float(change_pct),
        }
    except Exception as e:
        print(f"  [warn] failed to fetch {ticker}: {e}", file=sys.stderr)
        return None

def fetch_list(items):
    out = []
    for item in items:
        data = safe_fetch(item["ticker"])
        if data is None:
            continue
        out.append({**item, **data})
    return out

def pick_movers(items, n):
    """
    Daily rotation logic:
      - All `core: True` items are always included.
      - Remaining slots filled by biggest absolute % movers.
    Returns up to n items.
    """
    core = [i for i in items if i.get("core")]
    rest = [i for i in items if not i.get("core")]
    rest.sort(key=lambda x: abs(x.get("change_pct") or 0), reverse=True)
    picked = core + rest[: max(0, n - len(core))]
    # Final sort by change_pct descending so winners appear first
    picked.sort(key=lambda x: x.get("change_pct") or 0, reverse=True)
    return picked[:n]

# ============================================================
# Gemini narrative
# ============================================================

PROMPT_FULL = """你是一位專業的繁體中文財經分析師。根據以下市場數據，撰寫今日財經晨報的分析內容。請務必客觀、簡潔，繁體中文回答。

【日期】{date}（{weekday}），{city} 時間

【TSX 加拿大股市】 點位 {tsx_price}，漲跌 {tsx_pct}
【TAIEX 台灣股市】 點位 {taiex_price}，漲跌 {taiex_pct}

【TSX 主要走勢個股】
{tsx_top}

【TAIEX 主要走勢個股】
{taiex_top}

【總體市場】
{macro}

【投資組合持倉（僅供「今日相關觀察」分析，禁止透露金額/績效）】
{portfolio}

請回傳純 JSON（不要 markdown）：
{{
  "tsx_summary": "1-2 句 TSX 走勢摘要",
  "tsx_highlights": ["4 項簡短重點"],
  "taiex_summary": "1-2 句 TAIEX 走勢摘要",
  "taiex_highlights": ["4 項簡短重點"],
  "risks": ["強制 5 項風險"],
  "watch_points": ["強制 5 項觀察重點"],
  "suggestion": "1 段簡短建議",
  "portfolio_observations": ["5 項概念性觀察，禁止具體百分比/金額"],
  "position_health": ["4 項概念性部位健檢"]
}}"""

PROMPT_TW = """你是一位專業的繁體中文財經分析師。針對台灣家人撰寫今日財經晨報（純台股版本），客觀簡潔，繁體中文回答。

【日期】{date}（{weekday}），{city} 時間

【TAIEX 台灣股市】 點位 {taiex_price}，漲跌 {taiex_pct}

【TAIEX 主要走勢個股】
{taiex_top}

【總體市場（包含美股盤中走勢，影響台股次日開盤）】
{macro}

請回傳純 JSON（不要 markdown）：
{{
  "taiex_summary": "2-3 句 TAIEX 走勢摘要，要詳盡因為這是台灣家人最關心的部分",
  "taiex_highlights": ["5 項詳細重點，含族群分析"],
  "risks": ["強制 5 項風險（針對台股）"],
  "watch_points": ["強制 5 項觀察重點（針對台股次日）"],
  "suggestion": "1 段針對台股的簡短建議"
}}"""

def call_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[warn] GEMINI_API_KEY not set, using fallback narrative")
        return None
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[error] Gemini returned invalid JSON: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[error] Gemini call failed: {e}", file=sys.stderr)
        return None

def fallback_full(tsx, taiex):
    tsx_dir = "上漲" if (tsx and (tsx.get("change_pct") or 0) > 0) else "下跌"
    tw_dir  = "上漲" if (taiex and (taiex.get("change_pct") or 0) > 0) else "下跌"
    return {
        "tsx_summary": f"TSX 綜合指數今日{tsx_dir}，反映加拿大整體市場走勢。",
        "tsx_highlights": [
            "能源、金融、科技三大族群為主要影響",
            "留意 BoC 政策、油價與美元走勢",
            "個股表現分歧，可參考下方 Top 15 列表",
            "建議依個別投資目標進行配置調整",
        ],
        "taiex_summary": f"TAIEX 加權指數今日{tw_dir}，半導體與電子權值股影響顯著。",
        "taiex_highlights": [
            "TSMC 與 AI 概念股為主要焦點",
            "成交量與外資動向值得留意",
            "高股息與大盤 ETF 為穩健配置選擇",
            "建議搭配個股基本面評估",
        ],
        "risks": [
            "地緣政治風險可能推升避險需求",
            "通膨與利率政策路徑仍有不確定性",
            "AI/半導體股估值偏高，留意波動",
            "美元走強對非美資產形成壓力",
            "加密貨幣波動可能影響風險偏好",
        ],
        "watch_points": [
            "美股科技權值股能否帶量",
            "TSX 能源股表現是否續強",
            "台積電 ADR 表現對台股影響",
            "加拿大央行政策動向",
            "黃金與美元的避險拉鋸",
        ],
        "suggestion": "今日市場以個股表現為主，建議檢視持倉分散度，並關注後續經濟事件。",
        "portfolio_observations": [
            "AI/Tech 為主要部位：留意波動敏感度",
            "加拿大電信與公用事業為次要部位：利率敏感",
            "現金管理部位：提供穩定避險功能",
            "加密曝險：跟隨 BTC 波動",
            "全球分散部位：受惠國際分散",
        ],
        "position_health": [
            "集中度觀察：留意主要部位的市場敏感度",
            "表現落後標的：評估是否續抱",
            "表現強勁標的：可考慮再平衡",
            "產業分散度：科技、金融、電信、公用、現金五大領域",
        ],
    }

def fallback_tw(taiex):
    tw_dir = "上漲" if (taiex and (taiex.get("change_pct") or 0) > 0) else "下跌"
    return {
        "taiex_summary": f"TAIEX 加權指數今日{tw_dir}，半導體與電子權值股為主要驅動因素。國際資金動向與美股走勢將持續影響台股表現。",
        "taiex_highlights": [
            "TSMC 與 AI 概念股為主要關注焦點",
            "成交量與外資買賣超值得留意",
            "高股息族群為防禦性配置選擇",
            "電子權值股表現主導大盤走勢",
            "建議搭配個股基本面與技術面評估",
        ],
        "risks": [
            "地緣政治風險可能推升避險需求",
            "AI/半導體股估值偏高，留意波動",
            "美元走強對新台幣形成壓力",
            "外資動向影響台股短線表現",
            "全球景氣放緩對出口導向台股不利",
        ],
        "watch_points": [
            "台積電 ADR 美股表現對台股影響",
            "美股科技股能否續強帶動",
            "外資買賣超動向",
            "新台幣匯率走勢",
            "重要族群輪動方向",
        ],
        "suggestion": "今日台股走勢以權值股表現為主，建議檢視持股分散度，並關注後續國際事件與外資動向。",
    }

# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", choices=["full", "tw"], default="full")
    parser.add_argument("--date", help="Override report date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default=str(ROOT_DIR))
    args = parser.parse_args()

    region_cfg = config.REGIONS[args.region]
    tz = ZoneInfo(region_cfg["timezone"])

    if args.date:
        date_obj = dt.date.fromisoformat(args.date)
    else:
        date_obj = dt.datetime.now(tz).date()

    weekday_map = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    weekday_zh = weekday_map[date_obj.weekday()]
    date_str = date_obj.strftime("%Y/%m/%d")
    date_iso = date_obj.isoformat()

    print(f"=== {args.region.upper()} report: {date_iso} ({weekday_zh}) ===")

    # ---- Fetch (region-aware) ----
    print("[1/5] Fetching market data ...")

    taiex_index = safe_fetch(config.TAIEX_INDEX_TICKER)
    taiex_all   = fetch_list(config.TAIEX_UNIVERSE)
    tw_etfs_all = fetch_list(config.TAIEX_ETFS)
    macro       = fetch_list(config.MACRO)
    us_idx      = fetch_list(config.US_INDICES)

    taiex_top = pick_movers(taiex_all, region_cfg["top_taiex_n"])
    tw_etfs   = pick_movers(tw_etfs_all, region_cfg["etf_taiex_n"])

    tsx_index = None; tsx_top = []; ca_etfs = []; portfolio = []
    if args.region == "full":
        tsx_index   = safe_fetch(config.TSX_INDEX_TICKER)
        tsx_all     = fetch_list(config.TSX_UNIVERSE)
        ca_etfs_all = fetch_list(config.CANADA_ETFS)
        tsx_top   = pick_movers(tsx_all,   region_cfg["top_tsx_n"])
        ca_etfs   = pick_movers(ca_etfs_all, region_cfg["etf_ca_n"])
        portfolio = fetch_list(config.PORTFOLIO)
        for p in portfolio:
            arr, cls = arrow_for(p.get("change_pct"))
            p["arrow"] = arr; p["arrow_class"] = cls

    # ---- Gemini narrative ----
    print("[2/5] Calling Gemini for narrative ...")
    if args.region == "full":
        prompt = PROMPT_FULL.format(
            date=date_str, weekday=weekday_zh, city=region_cfg["city"],
            tsx_price=fmt_price(tsx_index.get("price")) if tsx_index else "—",
            tsx_pct=fmt_pct(tsx_index.get("change_pct")) if tsx_index else "—",
            taiex_price=fmt_price(taiex_index.get("price")) if taiex_index else "—",
            taiex_pct=fmt_pct(taiex_index.get("change_pct")) if taiex_index else "—",
            tsx_top="\n".join(f"- {s['ticker']} {s['name']}: {fmt_pct(s.get('change_pct'))}" for s in tsx_top),
            taiex_top="\n".join(f"- {s['ticker']} {s['name']}: {fmt_pct(s.get('change_pct'))}" for s in taiex_top),
            macro="\n".join(f"- {m['name']}: {fmt_price(m.get('price'))} ({fmt_pct(m.get('change_pct'))})" for m in macro),
            portfolio="\n".join(f"- {p['ticker']} {p['name']} {fmt_pct(p.get('change_pct'))}" for p in portfolio),
        )
        fallback_fn = lambda: fallback_full(tsx_index, taiex_index)
    else:
        prompt = PROMPT_TW.format(
            date=date_str, weekday=weekday_zh, city=region_cfg["city"],
            taiex_price=fmt_price(taiex_index.get("price")) if taiex_index else "—",
            taiex_pct=fmt_pct(taiex_index.get("change_pct")) if taiex_index else "—",
            taiex_top="\n".join(f"- {s['ticker']} {s['name']}: {fmt_pct(s.get('change_pct'))}" for s in taiex_top),
            macro="\n".join(f"- {m['name']}: {fmt_price(m.get('price'))} ({fmt_pct(m.get('change_pct'))})" for m in (macro + us_idx)),
        )
        fallback_fn = lambda: fallback_tw(taiex_index)

    narrative = call_gemini(prompt)
    if not narrative:
        print("  Using fallback narrative.")
        narrative = fallback_fn()

    # ---- Render ----
    print("[3/5] Rendering HTML ...")
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["pct"] = fmt_pct
    env.filters["price"] = fmt_price
    template = env.get_template("report.html.j2")

    # Section numbering map (only for sections that will render in this region)

    visible_sections = []

    if "tsx" in region_cfg["show_sections"]:
        visible_sections.append("tsx")

    if "taiex" in region_cfg["show_sections"]:
        visible_sections.append("taiex")

    if "etf_tw" in region_cfg["show_sections"] or "etf_ca" in region_cfg["show_sections"]:
        visible_sections.append("etf")

    if "top_tsx" in region_cfg["show_sections"] or "top_taiex" in region_cfg["show_sections"]:
        visible_sections.append("top")

    if "macro" in region_cfg["show_sections"]:
        visible_sections.append("macro")

    if "conclusion" in region_cfg["show_sections"]:
        visible_sections.append("conclusion")

    if "portfolio" in region_cfg["show_sections"]:
        visible_sections.append("portfolio")

    visible_sections.append("sources")

    nums = {
        section: idx
        for idx, section in enumerate(visible_sections, start=1)
    }

    html = template.render(
        region=args.region,
        show=set(region_cfg["show_sections"]),
        num=nums,
        city=region_cfg["city"],
        date_str=date_str, weekday_zh=weekday_zh,
        tsx=tsx_index, taiex=taiex_index,
        tsx_top=tsx_top, taiex_top=taiex_top,
        tw_etfs=tw_etfs, ca_etfs=ca_etfs,
        macro=macro, us_idx=us_idx,
        portfolio=portfolio, n=narrative,
        index_link=("../index.html" if args.region == "tw" else "index.html"),
    )

    # ---- Save ----
    print("[4/5] Saving HTML ...")
    out_root = Path(args.output_dir)
    subdir = region_cfg["output_subdir"]
    out_dir = out_root / subdir if subdir else out_root
    out_dir.mkdir(parents=True, exist_ok=True)
    html_filename = region_cfg["filename_fmt"].format(date=date_iso)
    output_path = out_dir / html_filename
    output_path.write_text(html, encoding="utf-8")
    print(f"  ✅ {output_path} ({output_path.stat().st_size:,} bytes)")

    # ---- latest.json for notifier ----
    print("[5/5] Writing latest.json ...")
    url = f"https://{config.USERNAME}.github.io/{config.REPO}/{region_cfg['url_path_fmt'].format(date=date_iso)}"
    summary = {
        "region":     args.region,
        "date":       date_iso,
        "date_str":   date_str,
        "weekday_zh": weekday_zh,
        "taiex":      taiex_index,
        "tsx":        tsx_index,
        "filename":   html_filename,
        "report_url": url,
    }
    summary_path = out_root / region_cfg["summary_path"]
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {summary_path}")
    print("Done.")

if __name__ == "__main__":
    main()
