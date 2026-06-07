# 🔄 升級到 v3 — 多區域 + 個人化版本

這次升級主要做 4 件事：

| 變更 | 內容 |
|------|------|
| 🌏 **多區域** | 加 8AM 跑 Jobi 完整版；台灣 8AM 跑家人台股版 |
| 📊 **動態 25 檔** | 台股、台 ETF 每日從 ~40/~30 候選池**自動輪動**挑出 25 檔（核心永遠保留） |
| 🔒 **個人化** | 家人看不到 TSX、加 ETF、投資組合 |
| 🤖 **Gemini 2.5 Flash** | 升級到目前免費 tier 的可用模型 |

---

## 📁 檔案變更總覽

```
daily-stock-reports/
├── .github/workflows/
│   ├── daily-report.yml          ← 覆蓋（改成 --region full）
│   └── daily-tw-report.yml       ← 新增！台灣 8AM 排程
├── scripts/
│   ├── config.py                 ← 覆蓋（擴大候選池 + REGIONS 設定）
│   ├── generate_daily_report.py  ← 覆蓋（加 --region 參數）
│   ├── notify_line.py            ← 覆蓋（加 --audience 參數 + multicast）
│   └── templates/report.html.j2  ← 覆蓋（區域感知模板）
├── tw/
│   └── index.html                ← 新增！家人首頁
└── index.html                    ← 覆蓋（同樣 UI，但精簡邏輯）
```

`requirements.txt` 沒變、`SETUP.md` 沒變。

---

## 🔑 Step 1：拿到廷宇的 LINE User ID

LINE Developers Console 沒辦法直接查別人的 User ID。最快方法：

### 方法 A：用 webhook.site（最簡單，5 分鐘）

1. 開 https://webhook.site → 自動產生一個你的專屬 URL（複製）
2. 開 [LINE Developers Console](https://developers.line.biz/console/) → 你的 channel → **Messaging API** 分頁
3. 找 **Webhook URL** → 貼上剛剛 webhook.site 的 URL → 點 **Update**
4. 點下方 **Use webhook** 開關打開（變綠色）
5. **請廷宇加你機器人為好友**（掃 QR code 加好友）
6. **請廷宇在 LINE 對話框打任何訊息**（例如「哈囉」）
7. 回到 webhook.site，會看到一筆 POST request 進來，找 JSON 裡這個欄位：
   ```json
   "source": {
     "userId": "U1234567890abcdef..."   ← 這就是廷宇的 LINE User ID
   }
   ```
8. **複製 userId**
9. 完成後**記得把 LINE webhook URL 移除**（或關閉 Use webhook 開關），避免 webhook.site 一直收 log

### 方法 B：自己寫 LINE Bot 回覆腳本

太複雜，跳過。方法 A 5 分鐘搞定。

---

## 🔐 Step 2：在 GitHub Secrets 新增

到 https://github.com/jobimtg/daily-stock-reports/settings/secrets/actions

點 **New repository secret**：

| Name | Value |
|------|------|
| `LINE_USER_IDS_TW_FAMILY` | 廷宇的 User ID（`U` 開頭那串） |

> 💡 **未來想加更多家人**：用逗號分隔，例如 `U1234,U5678,U9abc`。程式會自動用 multicast 一次發給所有人。

現在你的 secrets 應該有 4 個：
- ✅ `GEMINI_API_KEY`
- ✅ `LINE_CHANNEL_ACCESS_TOKEN`
- ✅ `LINE_USER_ID` (你自己的)
- ✅ `LINE_USER_IDS_TW_FAMILY` (廷宇的)

---

## 📤 Step 3：上傳 v3 檔案到 repo

從 `auto3.zip` 解壓出來的 7 個檔案要替換 / 新增：

| 動作 | 路徑 |
|------|------|
| 覆蓋 | `.github/workflows/daily-report.yml` |
| 新增 | `.github/workflows/daily-tw-report.yml` |
| 覆蓋 | `scripts/config.py` |
| 覆蓋 | `scripts/generate_daily_report.py` |
| 覆蓋 | `scripts/notify_line.py` |
| 覆蓋 | `scripts/templates/report.html.j2` |
| 覆蓋 | `index.html` |
| 新增 | `tw/index.html` |

**最簡單的方式：解壓 zip → 用 GitHub 網頁拖整個 `auto3/` 資料夾覆蓋**（GitHub 會自動合併）

---

## ▶️ Step 4：手動測試兩個 workflow

到 **Actions** tab：

1. **Daily Stock Report (Canada / Full)** → Run workflow
   - 等 ~1 分鐘
   - 完成後檢查 https://jobimtg.github.io/daily-stock-reports/
   - 你的 LINE 應收到一張卡片

2. **Daily Stock Report (Taiwan / TW family)** → Run workflow
   - 等 ~1 分鐘
   - 完成後檢查 https://jobimtg.github.io/daily-stock-reports/tw/
   - **廷宇的 LINE 應收到一張卡片**

---

## 🎯 之後每天會發生什麼

| 時間 | 動作 |
|------|------|
| **台灣 08:00**（UTC 00:00） | 家人版本自動生成 + 推 LINE 給廷宇 |
| **Vancouver 08:00**（UTC 15:00 PDT / 16:00 PST） | 你的完整版生成 + 推 LINE 給你 |

兩個 workflow 各跑各的，不會互相干擾。

---

## ❓ 常見問題

**Q：廷宇加機器人後我可以拿到 User ID 嗎？**
A：可以，但要透過 webhook 抓。LINE 不會直接顯示。所以才需要上面 Step 1 的步驟。

**Q：候選池要怎麼更動？**
A：直接編輯 `scripts/config.py`，commit 後下次跑就會用新的池子。

**Q：想多加家人怎麼辦？**
A：把廷宇的 User ID 加上家人的 User ID，用逗號分開放在 `LINE_USER_IDS_TW_FAMILY` secret 裡。例如 `U_廷宇,U_媽,U_爸`。

**Q：如果只想要某天不發給家人怎麼辦？**
A：到 Actions tab → Daily Stock Report (Taiwan) → ⋯ → Disable workflow。要恢復就 Enable。

**Q：core 標記的意思？**
A：`config.py` 裡某些 stock/ETF 有 `"core": True`，代表**永遠**會出現在報告裡（如台積電、0050）。其他 `core: False` 的會依當日波動度動態挑選。

---

✅ 設定完成後，整套自動化會穩穩跑下去。
