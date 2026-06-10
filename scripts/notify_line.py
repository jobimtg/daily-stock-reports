"""
LINE Messaging API Push Notification (v5 - tech blue carousel)
--------------------------------------------------------------
Flex Message design:
  1) Market Dashboard
  2) Today's Focus News
  3) Portfolio Performance
"""

import os
import sys
import json
import argparse
from pathlib import Path
import urllib.request
import urllib.error

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_MULTICAST_URL = "https://api.line.me/v2/bot/message/multicast"

# =========================
# Tech Blue Theme
# =========================
COLOR_BG_HEADER = "#071A2F"
COLOR_BG_BODY = "#0B2545"
COLOR_BG_FOOTER = "#071A2F"
COLOR_PANEL = "#123B63"
COLOR_PANEL_DARK = "#0E2F50"
COLOR_ACCENT = "#38BDF8"
COLOR_GREEN = "#22C55E"
COLOR_RED = "#F87171"
COLOR_FLAT = "#A8B2D1"
COLOR_TEXT = "#FFFFFF"
COLOR_MUTED = "#B8C7E0"
COLOR_LINE = "#1E5A8A"

AUDIENCE_CFG = {
    "me": {
        "summary_path": "latest.json",
        "target_env": "LINE_USER_ID",
        "mode": "push",
        "hero_icon": "🇨🇦",
        "card_title": "每日北美財經晨報",
        "card_subtitle": "Canada · US · Portfolio",
    },
    "tw_family": {
        "summary_path": "tw/latest.json",
        "target_env": "LINE_USER_IDS_TW_FAMILY",
        "mode": "multicast",
        "hero_icon": "🇹🇼",
        "card_title": "每日台股晨報",
        "card_subtitle": "Taiwan Market Daily Brief",
    },
    "tw_group": {
        "summary_path": "tw/latest.json",
        "target_env": "LINE_GROUP_ID",
        "mode": "push",
        "hero_icon": "🇹🇼",
        "card_title": "每日台股晨報",
        "card_subtitle": "Taiwan Market Daily Brief",
    },
}

def fmt_pct(p):
    if p is None:
        return "—"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"

def fmt_price(p):
    if p is None:
        return "—"
    return f"{p:,.2f}"

def color_for(pct):
    if pct is None or abs(pct) < 0.05:
        return COLOR_FLAT
    return COLOR_GREEN if pct > 0 else COLOR_RED

def arrow_for(pct):
    if pct is None or abs(pct) < 0.05:
        return "→"
    return "▲" if pct > 0 else "▼"

def trend_text(pct):
    if pct is None:
        return "資料更新中"
    if abs(pct) < 0.05:
        return "盤勢持平"
    return "上漲" if pct > 0 else "下跌"

def safe_text(value, default="—"):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default

def build_index_row(name_emoji, label, data):
    pct = data.get("change_pct") if data else None
    price = data.get("price") if data else None
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": COLOR_PANEL,
        "cornerRadius": "12px",
        "paddingAll": "12px",
        "spacing": "xs",
        "contents": [
            {"type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": f"{name_emoji} {label}", "size": "md", "color": COLOR_TEXT, "weight": "bold", "flex": 4},
                {"type": "text", "text": f"{arrow_for(pct)} {fmt_pct(pct)}", "size": "sm", "color": color_for(pct), "weight": "bold", "align": "end", "flex": 3},
            ]},
            {"type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": trend_text(pct), "size": "xs", "color": COLOR_MUTED, "flex": 3},
                {"type": "text", "text": fmt_price(price), "size": "xs", "color": COLOR_TEXT, "align": "end", "weight": "bold", "flex": 4},
            ]},
        ],
    }

def build_header(cfg, date_str, weekday_zh, page_label):
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": COLOR_BG_HEADER,
        "paddingAll": "16px",
        "spacing": "xs",
        "contents": [
            {"type": "text", "text": f"{cfg['hero_icon']} {cfg['card_title']}", "color": COLOR_TEXT, "size": "lg", "weight": "bold"},
            {"type": "text", "text": cfg["card_subtitle"], "color": COLOR_MUTED, "size": "xs"},
            {"type": "text", "text": f"{date_str}（{weekday_zh}） · {page_label}", "color": COLOR_ACCENT, "size": "xs", "weight": "bold"},
        ],
    }

def build_footer(url, label):
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": COLOR_BG_FOOTER,
        "paddingAll": "12px",
        "contents": [{
            "type": "button",
            "style": "primary",
            "height": "sm",
            "color": COLOR_ACCENT,
            "action": {"type": "uri", "label": label, "uri": url or "https://example.com"},
        }],
    }

def bubble_base(header, body_contents, footer):
    return {
        "type": "bubble",
        "size": "mega",
        "header": header,
        "body": {"type": "box", "layout": "vertical", "spacing": "md", "backgroundColor": COLOR_BG_BODY, "paddingAll": "16px", "contents": body_contents},
        "footer": footer,
        "styles": {"header": {"backgroundColor": COLOR_BG_HEADER}, "body": {"backgroundColor": COLOR_BG_BODY}, "footer": {"backgroundColor": COLOR_BG_FOOTER}},
    }

def normalize_news(summary):
    candidates = summary.get("news") or summary.get("top_news") or summary.get("focus_news") or summary.get("headlines") or []
    news_items = []
    if isinstance(candidates, list):
        for item in candidates[:3]:
            if isinstance(item, dict):
                title = item.get("title") or item.get("headline") or item.get("text")
                source = item.get("source") or item.get("publisher") or "Market News"
            else:
                title = str(item)
                source = "Market News"
            if title:
                news_items.append({"title": str(title), "source": str(source)})
    if not news_items:
        news_items = [
            {"title": "今日焦點新聞會依 latest.json 內容自動顯示", "source": "System"},
            {"title": "若 latest.json 沒有 news 欄位，這裡會先顯示預設文字", "source": "System"},
            {"title": "之後可在 generate_daily_report.py 加入 headlines/news 資料", "source": "System"},
        ]
    return news_items[:3]

def normalize_portfolio(summary):
    portfolio = summary.get("portfolio") or summary.get("portfolio_summary") or {}
    if not isinstance(portfolio, dict):
        portfolio = {}
    return {
        "total_value": portfolio.get("total_value") or portfolio.get("market_value") or summary.get("portfolio_value"),
        "day_change_pct": portfolio.get("day_change_pct") or portfolio.get("change_pct") or summary.get("portfolio_change_pct"),
        "top_winner": portfolio.get("top_winner") or portfolio.get("best") or summary.get("top_winner") or "資料更新中",
        "top_loser": portfolio.get("top_loser") or portfolio.get("worst") or summary.get("top_loser") or "資料更新中",
    }

def build_market_bubble(summary, audience):
    cfg = AUDIENCE_CFG[audience]
    date_str = summary.get("date_str", "")
    weekday_zh = summary.get("weekday_zh", "")
    url = summary.get("report_url", "")
    body_contents = [{"type": "text", "text": "Market Dashboard", "size": "sm", "color": COLOR_ACCENT, "weight": "bold"}]
    if summary.get("tsx") and audience == "me":
        body_contents.append(build_index_row("🇨🇦", "TSX", summary.get("tsx")))
    body_contents.append(build_index_row("🇹🇼", "TAIEX", summary.get("taiex")))
    body_contents.append({"type": "separator", "color": COLOR_LINE, "margin": "md"})
    body_contents.append({"type": "text", "text": "ETF · Top 15/25 · Macro · 投資組合", "size": "xxs", "color": COLOR_MUTED, "align": "center", "margin": "md"})
    return bubble_base(build_header(cfg, date_str, weekday_zh, "1/3 市場"), body_contents, build_footer(url, "查看完整報告"))

def build_news_bubble(summary, audience):
    cfg = AUDIENCE_CFG[audience]
    date_str = summary.get("date_str", "")
    weekday_zh = summary.get("weekday_zh", "")
    url = summary.get("report_url", "")
    body_contents = [{"type": "text", "text": "📰 今日焦點新聞", "size": "md", "color": COLOR_TEXT, "weight": "bold"}]
    for idx, item in enumerate(normalize_news(summary), start=1):
        body_contents.append({"type": "box", "layout": "vertical", "backgroundColor": COLOR_PANEL, "cornerRadius": "12px", "paddingAll": "12px", "spacing": "xs", "contents": [
            {"type": "text", "text": f"{idx}. {safe_text(item.get('title'))}", "size": "sm", "color": COLOR_TEXT, "weight": "bold", "wrap": True},
            {"type": "text", "text": safe_text(item.get("source"), "Market News"), "size": "xxs", "color": COLOR_MUTED, "wrap": True},
        ]})
    return bubble_base(build_header(cfg, date_str, weekday_zh, "2/3 新聞"), body_contents, build_footer(url, "閱讀完整新聞"))

def build_portfolio_bubble(summary, audience):
    cfg = AUDIENCE_CFG[audience]
    date_str = summary.get("date_str", "")
    weekday_zh = summary.get("weekday_zh", "")
    url = summary.get("report_url", "")
    p = normalize_portfolio(summary)
    change_pct = p["day_change_pct"]
    try:
        change_pct = float(change_pct) if change_pct is not None else None
    except Exception:
        change_pct = None
    try:
        total_text = f"${float(p['total_value']):,.2f}" if p["total_value"] is not None else "資料更新中"
    except Exception:
        total_text = safe_text(p["total_value"], "資料更新中")
    body_contents = [
        {"type": "text", "text": "💼 投資組合績效", "size": "md", "color": COLOR_TEXT, "weight": "bold"},
        {"type": "box", "layout": "vertical", "backgroundColor": COLOR_PANEL_DARK, "cornerRadius": "14px", "paddingAll": "14px", "spacing": "xs", "contents": [
            {"type": "text", "text": "目前市值", "size": "xs", "color": COLOR_MUTED},
            {"type": "text", "text": total_text, "size": "xxl", "color": COLOR_TEXT, "weight": "bold"},
            {"type": "text", "text": f"{arrow_for(change_pct)} 今日變化 {fmt_pct(change_pct)}", "size": "sm", "color": color_for(change_pct), "weight": "bold"},
        ]},
        {"type": "box", "layout": "vertical", "backgroundColor": COLOR_PANEL, "cornerRadius": "12px", "paddingAll": "12px", "spacing": "xs", "contents": [
            {"type": "text", "text": f"🏆 表現最佳：{safe_text(p['top_winner'], '資料更新中')}", "size": "sm", "color": COLOR_TEXT, "wrap": True},
            {"type": "text", "text": f"⚠️ 需要留意：{safe_text(p['top_loser'], '資料更新中')}", "size": "sm", "color": COLOR_TEXT, "wrap": True},
        ]},
    ]
    return bubble_base(build_header(cfg, date_str, weekday_zh, "3/3 投資組合"), body_contents, build_footer(url, "查看投資組合"))

def build_flex_message(summary, audience):
    cfg = AUDIENCE_CFG[audience]
    date_str = summary.get("date_str", "")
    return {
        "type": "flex",
        "altText": f"{cfg['hero_icon']} {cfg['card_title']} {date_str}",
        "contents": {
            "type": "carousel",
            "contents": [
                build_market_bubble(summary, audience),
                build_news_bubble(summary, audience),
                build_portfolio_bubble(summary, audience),
            ],
        },
    }

def post_json(url, payload, token):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[ok] LINE {url.rsplit('/', 1)[-1]}: {resp.status}")
            return True
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"[error] LINE API {e.code}: {err}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"[error] LINE connection failed: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audience", choices=["me", "tw_family", "tw_group"], required=True)
    args = parser.parse_args()
    cfg = AUDIENCE_CFG[args.audience]
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        print("[error] LINE_CHANNEL_ACCESS_TOKEN not set.", file=sys.stderr)
        return 1
    target_raw = os.environ.get(cfg["target_env"])
    if not target_raw:
        print(f"[error] {cfg['target_env']} not set.", file=sys.stderr)
        return 1
    summary_path = Path(cfg["summary_path"])
    if not summary_path.exists():
        print(f"[error] {summary_path} not found", file=sys.stderr)
        return 1
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    message = build_flex_message(summary, args.audience)
    if cfg["mode"] == "multicast":
        user_ids = [u.strip() for u in target_raw.split(",") if u.strip()]
        if not user_ids:
            print(f"[error] {cfg['target_env']} contains no valid user IDs.", file=sys.stderr)
            return 1
        payload = {"to": user_ids, "messages": [message]}
        ok = post_json(LINE_MULTICAST_URL, payload, token)
    else:
        payload = {"to": target_raw.strip(), "messages": [message]}
        ok = post_json(LINE_PUSH_URL, payload, token)
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
