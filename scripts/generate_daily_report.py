"""
Daily Stock Report Generator
-----------------------------
Fetches market data via yfinance, asks Gemini for narrative analysis,
renders an HTML report using a Jinja2 template, saves it, and also
writes `latest.json` for downstream notification (e.g. LINE).

GitHub Actions will commit & push the resulting HTML automatically.

Usage:
    python generate_daily_report.py
    python generate_daily_report.py --date 2026-06-04   # force a specific date

Requires:
    pip install yfinance google-generativeai jinja2

Env vars:
    GEMINI_API_KEY (required for AI narrative; falls back to template if missing)
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
    if p is None:
        return "—"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"

def fmt_price(p, decimals=2):
    if p is None:
        return "—"
    return f"{p:,.{decimals}f}"

def arrow_for(pct):
    if pct is None or abs(pct) < 0.05:
        return ("→", "flat")
    return ("↑", "up") if pct > 0 else ("↓", "down")

def safe_fetch(ticker, period="5d"):
    """Fetch latest close and percent change from previous close."""
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
            "ticker": ticker,
            "price": float(latest),
            "change": float(change),
            "change_pct": float(change_pct),
        }
    except Exception as e:
        print(f"  [warn] failed to fetch {ticker}: {e}", file=sys.stderr)
        return None

def fetch_list(items, ticker_key="ticker"):
    out = []
    for item in items:
        data = safe_fetch(item[ticker_key])
        if data is None:
            continue
        out.append({**item, **data})
    return out

def pick_etfs(all_etfs, n=15):
    """Core ETFs always; fill rest with biggest movers."""
    core = [e for e in all_etfs if e.get("core")]
    rest = [e for e in all_etfs if not e.get("core")]
    rest.sort(key=lambda e: abs(e.get("change_pct") or 0), reverse=True)
    picked = core + rest[: max(0, n - len(core))]
    picked.sort(key=lambda e: e.get("change_pct") or 0)
    return picked[:n]

# ============================================================
# Gemini narrative
# ============================================================

GEMINI_PROMPT_TEMPLATE = """你是一位專業的繁體中文財經分析師。根據以下市場數據，撰寫今日財經晨報的分析內容。請務必客觀、簡潔，並以繁體中文回答。

【今日日期】{date}（{weekday}），太平洋時間

【TSX 加拿大股市】
- 點位：{tsx_price}
- 漲跌幅：{tsx_pct}

【TAIEX 台灣股市】
- 點位：{taiex_price}
- 漲跌幅：{taiex_pct}

【TSX 主要走勢個股】
{tsx_top}

【TAIEX 主要走勢個股】
{taiex_top}

【總體市場】
{macro}

【投資組合持倉（僅作為「今日相關觀察」分析參考，禁止透露金額/績效）】
{portfolio}

請以 JSON 格式回覆（**只回 JSON，不要任何 markdown code fence**），包含以下欄位：

{{
  "tsx_summary": "1-2 句 TSX 走勢摘要，繁體中文",
  "tsx_highlights": ["重點1（簡短）", "重點2", "重點3", "重點4"],
  "taiex_summary": "1-2 句 TAIEX 走勢摘要，繁體中文",
  "taiex_highlights": ["重點1", "重點2", "重點3", "重點4"],
  "risks": ["市場風險1", "風險2", "風險3", "風險4", "風險5"],
  "watch_points": ["今日觀察1", "觀察2", "觀察3", "觀察4", "觀察5"],
  "suggestion": "1 段簡短建議，繁體中文",
  "portfolio_observations": [
    "概念性觀察1，例如 'AI/Tech 為主要部位（NVDA、SMCI）：...'，禁止具體百分比",
    "觀察2", "觀察3", "觀察4", "觀察5"
  ],
  "position_health": [
    "集中度觀察：...",
    "表現落後標的：...",
    "表現強勁標的：...",
    "產業分散度：..."
  ]
}}

注意事項：
- 投資組合區段絕不可出現任何 CAD 金額、損益百分比、配置比例
- 用 "主要部位"、"次要部位"、"防禦性配置" 等模糊描述
- 風險與觀察重點各「強制 5 項」
"""

def call_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[warn] GEMINI_API_KEY not set, using fallback narrative")
        return None
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
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

def build_gemini_prompt(date_str, weekday_zh, tsx, taiex, tsx_top, taiex_top, macro, portfolio):
    def f_stock(s): return f"- {s['ticker']} {s['name']}: {fmt_pct(s.get('change_pct'))}（{s.get('sector','')})"
    def f_macro(m): return f"- {m['name']}: {fmt_price(m.get('price'))} {m.get('unit','')} ({fmt_pct(m.get('change_pct'))})"
    def f_port(p):  return f"- {p['ticker']} {p['name']} {fmt_pct(p.get('change_pct'))}"
    return GEMINI_PROMPT_TEMPLATE.format(
        date=date_str, weekday=weekday_zh,
        tsx_price=fmt_price(tsx.get("price")) if tsx else "—",
        tsx_pct=fmt_pct(tsx.get("change_pct")) if tsx else "—",
        taiex_price=fmt_price(taiex.get("price")) if taiex else "—",
        taiex_pct=fmt_pct(taiex.get("change_pct")) if taiex else "—",
        tsx_top="\n".join(f_stock(s) for s in tsx_top[:15]),
        taiex_top="\n".join(f_stock(s) for s in taiex_top[:15]),
        macro="\n".join(f_macro(m) for m in macro),
        portfolio="\n".join(f_port(p) for p in portfolio),
    )

def fallback_narrative(tsx, taiex):
    tsx_dir = "上漲" if (tsx and (tsx.get("change_pct") or 0) > 0) else "下跌"
    tw_dir  = "上漲" if (taiex and (taiex.get("change_pct") or 0) > 0) else "下跌"
    return {
        "tsx_summary": f"TSX 綜合指數今日{tsx_dir}，反映加拿大整體市場走勢。",
        "tsx_highlights": [
            "能源、金融、科技三大族群為主要影響因素",
            "留意 BoC 政策、油價與美元走勢",
            "個股表現分歧，可參考下方 Top 15 列表",
            "建議依個別投資目標進行配置調整",
        ],
        "taiex_summary": f"TAIEX 加權指數今日{tw_dir}，半導體與電子權值股影響顯著。",
        "taiex_highlights": [
            "TSMC 與 AI 概念股為主要關注焦點",
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

# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Override report date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default=str(ROOT_DIR), help="Output directory")
    args = parser.parse_args()

    pt = ZoneInfo(config.TIMEZONE)
    if args.date:
        date_obj = dt.date.fromisoformat(args.date)
    else:
        date_obj = dt.datetime.now(pt).date()

    weekday_map = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    weekday_zh = weekday_map[date_obj.weekday()]
    date_str = date_obj.strftime("%Y/%m/%d")
    date_iso = date_obj.isoformat()

    print(f"=== Daily Stock Report: {date_iso} ({weekday_zh}) ===")

    print("[1/5] Fetching market data ...")
    tsx_index   = safe_fetch(config.TSX_INDEX_TICKER)
    taiex_index = safe_fetch(config.TAIEX_INDEX_TICKER)
    tsx_top     = fetch_list(config.TSX_TOP15)
    taiex_top   = fetch_list(config.TAIEX_TOP15)
    tw_etfs_all = fetch_list(config.TAIEX_ETFS)
    ca_etfs_all = fetch_list(config.CANADA_ETFS)
    tw_etfs     = pick_etfs(tw_etfs_all, 15)
    ca_etfs     = pick_etfs(ca_etfs_all, 15)
    macro       = fetch_list(config.MACRO)
    us_idx      = fetch_list(config.US_INDICES)
    portfolio   = fetch_list(config.PORTFOLIO)

    tsx_top.sort(key=lambda s: s.get("change_pct") or 0, reverse=True)
    taiex_top.sort(key=lambda s: s.get("change_pct") or 0, reverse=True)

    for p in portfolio:
        arr, cls = arrow_for(p.get("change_pct"))
        p["arrow"] = arr
        p["arrow_class"] = cls

    print("[2/5] Calling Gemini for narrative ...")
    prompt = build_gemini_prompt(date_str, weekday_zh, tsx_index, taiex_index,
                                 tsx_top, taiex_top, macro, portfolio)
    narrative = call_gemini(prompt)
    if not narrative:
        print("  Using fallback narrative.")
        narrative = fallback_narrative(tsx_index, taiex_index)

    print("[3/5] Rendering HTML ...")
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["pct"] = fmt_pct
    env.filters["price"] = fmt_price
    template = env.get_template("report.html.j2")
    html = template.render(
        date_str=date_str, weekday_zh=weekday_zh,
        tsx=tsx_index, taiex=taiex_index,
        tsx_top=tsx_top, taiex_top=taiex_top,
        tw_etfs=tw_etfs, ca_etfs=ca_etfs,
        macro=macro, us_idx=us_idx,
        portfolio=portfolio, n=narrative,
    )

    print("[4/5] Saving HTML ...")
    html_filename = f"daily-financial-brief-{date_iso}.html"
    output_path = Path(args.output_dir) / html_filename
    output_path.write_text(html, encoding="utf-8")
    print(f"  ✅ {output_path} ({output_path.stat().st_size:,} bytes)")

    print("[5/5] Writing latest.json for downstream notification ...")
    summary = {
        "date":       date_iso,
        "date_str":   date_str,
        "weekday_zh": weekday_zh,
        "tsx":        tsx_index,
        "taiex":      taiex_index,
        "filename":   html_filename,
        "report_url": f"https://{config.USERNAME}.github.io/{config.REPO}/{html_filename}",
    }
    latest_path = Path(args.output_dir) / "latest.json"
    latest_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {latest_path}")

    print("Done.")

if __name__ == "__main__":
    main()
