"""
LINE Messaging API Push Notification (v3 - multi-audience)
-----------------------------------------------------------
Sends a Flex Message card to the appropriate audience.

  --audience me         → reads LINE_USER_ID, summary from latest.json
  --audience tw_family  → reads LINE_USER_IDS_TW_FAMILY (comma-separated),
                           summary from tw/latest.json

Env vars:
    LINE_CHANNEL_ACCESS_TOKEN (required)
    LINE_USER_ID              (for --audience me)
    LINE_USER_IDS_TW_FAMILY   (for --audience tw_family, comma-separated)
"""

import os
import sys
import json
import argparse
from pathlib import Path
import urllib.request
import urllib.error

LINE_PUSH_URL      = "https://api.line.me/v2/bot/message/push"
LINE_MULTICAST_URL = "https://api.line.me/v2/bot/message/multicast"

COLOR_BG_HEADER = "#1a1a2e"
COLOR_ACCENT    = "#64ffda"
COLOR_GREEN     = "#51cf66"
COLOR_RED       = "#ff6b6b"
COLOR_FLAT      = "#a8b2d1"
COLOR_TEXT      = "#ffffff"

AUDIENCE_CFG = {
    "me": {
        "summary_path": "latest.json",
        "user_id_env":  "LINE_USER_ID",
        "is_multicast": False,
        "card_title":   "📈 每日財經晨報",
        "card_subtitle":"完整版（含投資組合）",
    },
    "tw_family": {
        "summary_path": "tw/latest.json",
        "user_id_env":  "LINE_USER_IDS_TW_FAMILY",
        "is_multicast": True,
        "card_title":   "📈 每日台股晨報",
        "card_subtitle":"Taiwan Market Daily Brief",
    },
}

# ─── Formatting ───
def fmt_pct(p):
    if p is None: return "—"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"

def fmt_price(p):
    if p is None: return "—"
    return f"{p:,.2f}"

def color_for(pct):
    if pct is None or abs(pct) < 0.05: return COLOR_FLAT
    return COLOR_GREEN if pct > 0 else COLOR_RED

def arrow_for(pct):
    if pct is None or abs(pct) < 0.05: return "→"
    return "▲" if pct > 0 else "▼"

# ─── Flex builders ───
def build_index_row(name_emoji, label, data):
    pct = data.get("change_pct") if data else None
    return {
        "type": "box", "layout": "horizontal", "spacing": "sm",
        "contents": [
            {"type": "text", "text": f"{name_emoji} {label}",
             "size": "sm", "color": "#a8b2d1", "flex": 3},
            {"type": "text", "text": fmt_price(data.get("price")) if data else "—",
             "size": "sm", "color": COLOR_TEXT, "weight": "bold", "align": "end", "flex": 3},
            {"type": "text", "text": f"{arrow_for(pct)} {fmt_pct(pct)}",
             "size": "sm", "color": color_for(pct), "weight": "bold", "align": "end", "flex": 3},
        ],
    }

def build_flex_message(summary, audience):
    cfg = AUDIENCE_CFG[audience]
    date_str   = summary.get("date_str", "")
    weekday_zh = summary.get("weekday_zh", "")
    tsx        = summary.get("tsx")
    taiex      = summary.get("taiex")
    url        = summary.get("report_url", "")

    body_contents = []
    if tsx and audience == "me":
        body_contents.append(build_index_row("🇨🇦", "TSX", tsx))
        body_contents.append({"type": "separator", "color": "#2a3a5e"})
    body_contents.append(build_index_row("🇹🇼", "TAIEX", taiex))
    body_contents.append({
        "type": "text",
        "text": ("ETF · Top 15/25 · Macro · 投資組合" if audience == "me"
                 else "ETF 25 · Top 25 · Macro"),
        "size": "xxs", "color": "#6e7891", "align": "center", "margin": "md",
    })

    bubble = {
        "type": "bubble", "size": "kilo",
        "header": {
            "type": "box", "layout": "vertical",
            "backgroundColor": COLOR_BG_HEADER, "paddingAll": "16px", "spacing": "xs",
            "contents": [
                {"type": "text", "text": cfg["card_title"],
                 "color": COLOR_TEXT, "size": "lg", "weight": "bold"},
                {"type": "text", "text": f"{date_str}（{weekday_zh}）",
                 "color": COLOR_ACCENT, "size": "xs"},
            ],
        },
        "body": {
            "type": "box", "layout": "vertical", "spacing": "md",
            "backgroundColor": "#16213e", "paddingAll": "16px",
            "contents": body_contents,
        },
        "footer": {
            "type": "box", "layout": "vertical",
            "backgroundColor": "#0f3460", "paddingAll": "12px",
            "contents": [{
                "type": "button", "style": "primary", "color": COLOR_ACCENT,
                "action": {"type": "uri", "label": "查看完整報告", "uri": url},
            }],
        },
        "styles": {
            "header": {"backgroundColor": COLOR_BG_HEADER},
            "body":   {"backgroundColor": "#16213e"},
            "footer": {"backgroundColor": "#0f3460"},
        },
    }
    return {
        "type": "flex",
        "altText": f"{cfg['card_title']} {date_str}",
        "contents": bubble,
    }

# ─── HTTP ───
def post_json(url, payload, token):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[ok] LINE {url.rsplit('/',1)[-1]}: {resp.status}")
            return True
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"[error] LINE API {e.code}: {err}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"[error] LINE connection failed: {e}", file=sys.stderr)
        return False

# ─── Main ───
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audience", choices=["me", "tw_family"], required=True)
    args = parser.parse_args()

    cfg = AUDIENCE_CFG[args.audience]
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        print("[skip] LINE_CHANNEL_ACCESS_TOKEN not set.")
        return 0

    user_id_raw = os.environ.get(cfg["user_id_env"])
    if not user_id_raw:
        print(f"[skip] {cfg['user_id_env']} not set.")
        return 0

    summary_path = Path(cfg["summary_path"])
    if not summary_path.exists():
        print(f"[error] {summary_path} not found", file=sys.stderr)
        return 1

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    message = build_flex_message(summary, args.audience)

    user_ids = [u.strip() for u in user_id_raw.split(",") if u.strip()]
    if not user_ids:
        print(f"[skip] {cfg['user_id_env']} contains no valid user IDs.")
        return 0

    if cfg["is_multicast"] or len(user_ids) > 1:
        # Use multicast for >1 recipient
        payload = {"to": user_ids, "messages": [message]}
        ok = post_json(LINE_MULTICAST_URL, payload, token)
    else:
        payload = {"to": user_ids[0], "messages": [message]}
        ok = post_json(LINE_PUSH_URL, payload, token)

    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
