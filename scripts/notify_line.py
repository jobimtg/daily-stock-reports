"""
LINE Messaging API Push Notification
-------------------------------------
Reads `latest.json` (written by generate_daily_report.py) and sends
a Flex Message card to your LINE account with a button to open the report.

Env vars required:
    LINE_CHANNEL_ACCESS_TOKEN  — long-lived channel access token
    LINE_USER_ID               — your LINE user ID (starts with "U...")

Usage:
    python scripts/notify_line.py
    python scripts/notify_line.py --json /path/to/latest.json
"""

import os
import sys
import json
import argparse
from pathlib import Path
import urllib.request
import urllib.error

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"

# ─── Colors ──────────────────────────────────────────────
COLOR_BG_HEADER = "#1a1a2e"
COLOR_ACCENT    = "#64ffda"
COLOR_GREEN     = "#51cf66"
COLOR_RED       = "#ff6b6b"
COLOR_FLAT      = "#a8b2d1"
COLOR_TEXT      = "#ffffff"


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


def build_index_row(name_emoji, label, data):
    """One row showing index name, price, arrow, change."""
    pct = data.get("change_pct") if data else None
    return {
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [
            {
                "type": "text",
                "text": f"{name_emoji} {label}",
                "size": "sm",
                "color": "#a8b2d1",
                "flex": 3,
            },
            {
                "type": "text",
                "text": fmt_price(data.get("price")) if data else "—",
                "size": "sm",
                "color": COLOR_TEXT,
                "weight": "bold",
                "align": "end",
                "flex": 3,
            },
            {
                "type": "text",
                "text": f"{arrow_for(pct)} {fmt_pct(pct)}",
                "size": "sm",
                "color": color_for(pct),
                "weight": "bold",
                "align": "end",
                "flex": 3,
            },
        ],
    }


def build_flex_message(summary):
    """Build a Flex Message bubble from the summary dict."""
    date_str   = summary.get("date_str", "")
    weekday_zh = summary.get("weekday_zh", "")
    tsx        = summary.get("tsx")
    taiex      = summary.get("taiex")
    url        = summary.get("report_url", "")

    bubble = {
        "type": "bubble",
        "size": "kilo",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": COLOR_BG_HEADER,
            "paddingAll": "16px",
            "spacing": "xs",
            "contents": [
                {
                    "type": "text",
                    "text": "📈 每日財經晨報",
                    "color": COLOR_TEXT,
                    "size": "lg",
                    "weight": "bold",
                },
                {
                    "type": "text",
                    "text": f"{date_str}（{weekday_zh}）",
                    "color": COLOR_ACCENT,
                    "size": "xs",
                },
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "backgroundColor": "#16213e",
            "paddingAll": "16px",
            "contents": [
                build_index_row("🇨🇦", "TSX",   tsx),
                {"type": "separator", "color": "#2a3a5e"},
                build_index_row("🇹🇼", "TAIEX", taiex),
                {
                    "type": "text",
                    "text": "ETF · Top 15 · Macro · 投資組合",
                    "size": "xxs",
                    "color": "#6e7891",
                    "align": "center",
                    "margin": "md",
                },
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#0f3460",
            "paddingAll": "12px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": COLOR_ACCENT,
                    "action": {
                        "type": "uri",
                        "label": "查看完整報告",
                        "uri": url,
                    },
                }
            ],
        },
        "styles": {
            "header": {"backgroundColor": COLOR_BG_HEADER},
            "body":   {"backgroundColor": "#16213e"},
            "footer": {"backgroundColor": "#0f3460"},
        },
    }

    return {
        "type": "flex",
        "altText": f"📈 每日財經晨報 {date_str}",
        "contents": bubble,
    }


def push_to_line(payload, token):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LINE_PUSH_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[ok] LINE responded: {resp.status} {resp.reason}")
            return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"[error] LINE API HTTP {e.code}: {err_body}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"[error] LINE API connection failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json", default="latest.json",
        help="Path to the summary JSON file (default: latest.json)",
    )
    args = parser.parse_args()

    token   = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    if not token:
        print("[skip] LINE_CHANNEL_ACCESS_TOKEN not set — skipping notification.")
        return 0
    if not user_id:
        print("[skip] LINE_USER_ID not set — skipping notification.")
        return 0

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"[error] Summary file not found: {json_path}", file=sys.stderr)
        return 1

    summary = json.loads(json_path.read_text(encoding="utf-8"))
    message = build_flex_message(summary)

    payload = {
        "to": user_id,
        "messages": [message],
    }

    ok = push_to_line(payload, token)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
