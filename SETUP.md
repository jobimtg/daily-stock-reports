# 🚀 設定指南：完全自動化每日財經報告

整個流程設定一次，**之後永遠不用碰**。每天早上 8:00 PT GitHub Actions 自動執行，生成報告 push 到 repo，你打開首頁就能看到。

---

## 📋 你會用到的服務（全部免費）

| 服務 | 用途 | 費用 |
|------|------|------|
| GitHub Pages | 報告 hosting | $0 |
| GitHub Actions | 自動執行 | $0（公開 repo 無限額） |
| yfinance | 股市資料 | $0（無 API key） |
| Google Gemini API | 分析文字 | $0（Free tier，每日 1500 次絕對夠用） |

**總成本：每月 $0**

---

## 🔑 Step 1：取得 Gemini API Key（2 分鐘）

1. 開啟 https://aistudio.google.com/app/apikey
2. 用 Google 帳號登入
3. 點 **"Create API key"**
4. 選 **"Create API key in new project"**（或選你已有的 project）
5. 複製產生的 API key（一串長字母數字，**只會顯示一次，記得先存起來**）

---

## 🔐 Step 2：把 API Key 加到 GitHub Secrets（1 分鐘）

1. 開啟你的 repo：https://github.com/jobimtg/daily-stock-reports
2. 點 **Settings**（在 repo 上方那排）
3. 左側選單找 **Secrets and variables → Actions**
4. 點 **New repository secret**
5. Name 欄填：`GEMINI_API_KEY`
6. Value 欄貼上剛剛複製的 API key
7. 點 **Add secret**

✅ 這個 key 只有 GitHub Actions 能存取，不會出現在 repo 程式碼裡，也不會被別人看到。

---

## 📦 Step 3：上傳所有檔案到 repo（3 分鐘）

你需要把整個 `auto/` 資料夾的內容**保持資料夾結構**上傳到 repo 根目錄。

### 推薦方法：直接 commit 整個 zip 解壓後的內容

我會準備好一個 zip 給你。下載後解壓，會看到這個結構：

```
daily-stock-reports/
├── .github/
│   └── workflows/
│       └── daily-report.yml      ← GitHub Actions 設定
├── scripts/
│   ├── config.py                 ← 持倉清單與 ETF 名單（你日後可修改）
│   ├── generate_daily_report.py  ← 主程式
│   └── templates/
│       └── report.html.j2        ← HTML 樣板
├── requirements.txt              ← Python 套件清單
├── index.html                    ← 首頁（已存在，不用覆蓋）
└── (未來每天會自動生成)
    daily-financial-brief-YYYY-MM-DD.html
```

### 上傳步驟

1. 開啟 https://github.com/jobimtg/daily-stock-reports
2. 點 **Add file → Upload files**
3. **把整個 `auto/` 資料夾內所有檔案、保持子資料夾結構，整批拖到 GitHub**
   - 或一個一個資料夾上傳：先建 `.github/workflows/`，再建 `scripts/templates/`，最後上傳 `requirements.txt`
4. 下方 commit message 填：`Setup GitHub Actions automation`
5. 點 **Commit changes**

---

## ▶️ Step 4：第一次手動測試（30 秒）

1. 點 repo 上方的 **Actions** tab
2. 左側選 **Daily Stock Report**
3. 右上點 **Run workflow → Run workflow**
4. 等 1–2 分鐘
5. 重新整理頁面，看到綠色勾勾 ✅ 代表成功
6. 回 repo 首頁，會看到新檔案 `daily-financial-brief-YYYY-MM-DD.html`
7. 打開 https://jobimtg.github.io/daily-stock-reports/ 應該看到首頁列出今日報告

---

## 🎉 Step 5：完成！

之後每天 **8:00 AM 太平洋時間**，GitHub Actions 自動：

1. 啟動執行環境
2. 安裝 Python 套件
3. yfinance 抓取最新市場資料
4. Gemini AI 生成繁體中文分析
5. 渲染 HTML
6. Commit + push 到 repo
7. GitHub Pages 自動更新

你**完全不用做任何事**，每天打開首頁就有報告。

---

## 🛠 日常維護

### 持倉變動時
編輯 `scripts/config.py` 裡的 `PORTFOLIO` 清單，commit 即可。

### ETF 名單想換
編輯 `scripts/config.py` 裡的 `TAIEX_ETFS` 或 `CANADA_ETFS`。

### 想調整時間
編輯 `.github/workflows/daily-report.yml` 裡的 `cron` 設定。
- `0 15 * * *` = UTC 15:00 = PDT 08:00 / PST 07:00
- `0 16 * * *` = UTC 16:00 = PDT 09:00 / PST 08:00

### 想暫停自動化
到 **Actions → Daily Stock Report → ⋯ → Disable workflow**

### 重啟
**Actions → Daily Stock Report → ⋯ → Enable workflow**

---

## ❓ 故障排除

**Q：Actions 跑失敗了**
A：到 Actions tab 點失敗的執行 → 看紅色 step 的 log。最常見問題：
- API key 拼錯 → 回 Secrets 重新貼一次
- yfinance 暫時抓不到資料 → 多試幾次
- 某個 ticker 失效 → 編輯 `config.py` 拿掉

**Q：報告文字呆呆的**
A：表示 Gemini 那次 call 失敗，腳本自動 fallback 到模板文字。檢查 Gemini quota 或 API key。

**Q：今天沒有報告**
A：先檢查 Actions 是否有跑（綠勾），再檢查是否 push 到 main branch。

---

## 🧪 本地測試（選用）

如果你想在電腦上先測試一下：

```bash
git clone https://github.com/jobimtg/daily-stock-reports.git
cd daily-stock-reports
pip install -r requirements.txt
export GEMINI_API_KEY="你的key"
python scripts/generate_daily_report.py
```

會在當前目錄產生 `daily-financial-brief-YYYY-MM-DD.html`，用瀏覽器打開就能看。

---

## 🎯 後續可加功能

- [ ] 每週日自動生成消費報告（需要結合 Google Sheets 或其他來源）
- [ ] 每月 1 號自動生成月度財務分析
- [ ] LINE Notify 自動發送報告連結
- [ ] 加上 Email 通知

任何時候有需求，直接告訴我，可以再擴充。

