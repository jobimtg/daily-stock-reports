"""
LINE Messaging API Push Notification (v5 - individual, family multicast, group)
-------------------------------------------------------------------------------
Audiences:
  --audience me         -> LINE_USER_ID, canada/latest.json
  --audience tw_family  -> LINE_USER_IDS_TW_FAMILY, taiwan/latest.json
  --audience tw_group   -> LINE_GROUP_ID, taiwan/latest.json

Features:
  - Uses new canada/ and taiwan/ summary paths.
  - Prevents duplicate pushes for the same audience/date.
  - Use LINE_FORCE_PUSH=true to intentionally send again.
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
PUSH_LOG_PATH = Path("cache/line_push_log.json")

COLOR_BG_HEADER = "#1a1a2e"
COLOR_ACCENT = "#64ffda"
COLOR_GREEN = "#51cf66"
COLOR_RED = "#ff6b6b"
COLOR_FLAT = "#a8b2d1"
COLOR_TEXT = "#ffffff"

AUDIENCE_CFG = {
    "me": {
        "summary_path": "canada/latest.json",
        "target_env": "LINE_USER_ID",
        "mode": "push",
        "card_title": "📈 每日北美財經晨報",
        "card_subtitle": "完整版（含投資組合）",
    },
    "tw_family": {
        "summary_path": "taiwan/latest.json",
        "target_env": "LINE_USER_IDS_TW_FAMILY",
        "mode": "multicast",
        "card_title": "📈 每日台股晨報",
        "card_subtitle": "Taiwan Market Daily Brief",
    },
    "tw_group": {
        "summary_path": "taiwan/latest.json",
        "target_env": "LINE_GROUP_ID",
        "mode": "push",
        "card_title": "📈 每日台股晨報",
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


def read_push_log():
    if not PUSH_LOG_PATH.exists():
        return {}
    try:
        return json.loads(PUSH_LOG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_push_log(log):
    PUSH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUSH_LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def build_index_row(name_emoji, label, data):
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


def build_flex_message(summary, audience):
    cfg = AUDIENCE_CFG[audience]
    date_str = summary.get("date_str", "")
    weekday_zh = summary.get("weekday_zh", "")
    tsx = summary.get("tsx")
    taiex = summary.get("taiex")
    url = summary.get("report_url", "")

    body_contents = []
    if tsx and audience == "me":
        body_contents.append(build_index_row("🇨🇦", "TSX", tsx))
        body_contents.append({"type": "separator", "color": "#2a3a5e"})

    body_contents.append(build_index_row("🇹🇼", "TAIEX", taiex))
    body_contents.append({
        "type": "text",
        "text": "ETF 25 · Top 25 · Macro" if audience in ("tw_family", "tw_group") else "ETF · Top 15/25 · Macro · 投資組合",
        "size": "xxs",
        "color": "#6e7891",
        "align": "center",
        "margin": "md",
    })

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
                    "text": cfg["card_title"],
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
            "contents": body_contents,
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
            "body": {"backgroundColor": "#16213e"},
            "footer": {"backgroundColor": "#0f3460"},
        },
    }

    return {
        "type": "flex",
        "altText": f"{cfg['card_title']} {date_str}",
        "contents": bubble,
    }


def post_json(url, payload, token):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

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
    report_date = summary.get("date", "unknown-date")
    push_key = f"{args.audience}:{report_date}"
    force_push = os.environ.get("LINE_FORCE_PUSH", "false").lower() == "true"

    push_log = read_push_log()
    if push_key in push_log and not force_push:
        print(f"[skip] LINE already pushed for {push_key}. Set LINE_FORCE_PUSH=true to send again.")
        return 0

    message = build_flex_message(summary, args.audience)

    if cfg["mode"] == "multicast":
        user_ids = [u.strip() for u in target_raw.split(",") if u.strip()]
        if not user_ids:
            print(f"[error] {cfg['target_env']} contains no valid user IDs.", file=sys.stderr)
            return 1
        payload = {"to": user_ids, "messages": [message]}
        ok = post_json(LINE_MULTICAST_URL, payload, token)
    else:
        target = target_raw.strip()
        payload = {"to": target, "messages": [message]}
        ok = post_json(LINE_PUSH_URL, payload, token)

    if ok:
        push_log[push_key] = {
            "audience": args.audience,
            "date": report_date,
            "report_url": summary.get("report_url", ""),
        }
        write_push_log(push_log)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
