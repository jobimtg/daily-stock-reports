"""
Configuration for the daily stock report.
Edit this file to update your watchlists or portfolio holdings.
"""

# ============================================================
# Investment Portfolio (just tickers + display names — no dollar amounts)
# Update this list whenever your holdings change.
# ============================================================
PORTFOLIO = [
    # ticker (for yfinance), display name, type
    {"ticker": "NVDA",      "name": "Nvidia CDR (Hedged)",       "type": "CDR"},
    {"ticker": "SMCI",      "name": "Supermicro CDR (Hedged)",   "type": "CDR"},
    {"ticker": "BCE.TO",    "name": "BCE Inc",                   "type": "TSX"},
    {"ticker": "PDIV.TO",   "name": "Purpose Enhanced Dividend", "type": "ETF"},
    {"ticker": "AQN.TO",    "name": "Algonquin Power & Util",    "type": "TSX"},
    {"ticker": "PSA.TO",    "name": "Purpose HISA ETF",          "type": "ETF"},
    {"ticker": "XEQT.TO",   "name": "iShares Core Equity ETF",   "type": "ETF"},
    {"ticker": "BTCC.TO",   "name": "Purpose Bitcoin ETF (Hdg)", "type": "ETF"},
    {"ticker": "T.TO",      "name": "Telus Corp",                "type": "TSX"},
    {"ticker": "LB.TO",     "name": "Laurentian Bank",           "type": "TSX"},
    {"ticker": "SOBO.TO",   "name": "South Bow Corp",            "type": "TSX"},
]

# Note about CDRs:
# NVDA and SMCI as CDRs on Cboe Canada use special tickers like "NVDA.NE".
# yfinance support varies — if data is missing, the script will fall back
# to the underlying US ticker (NVDA, SMCI) for price reference.

# ============================================================
# TAIEX ETF universe (15 ETFs — script picks daily based on relevance)
# Always-include core: 0050, 0056, 00878
# ============================================================
TAIEX_ETFS = [
    {"ticker": "0050.TW",   "name": "元大台灣 50",          "category": "大盤",       "core": True},
    {"ticker": "006208.TW", "name": "富邦台 50",            "category": "大盤",       "core": False},
    {"ticker": "0056.TW",   "name": "元大高股息",           "category": "高股息",     "core": True},
    {"ticker": "00878.TW",  "name": "國泰永續高股息",       "category": "ESG 高息",   "core": True},
    {"ticker": "00919.TW",  "name": "群益台灣精選高息",     "category": "高股息",     "core": False},
    {"ticker": "00929.TW",  "name": "復華台灣科技優息",     "category": "科技+息",    "core": False},
    {"ticker": "00891.TW",  "name": "中信關鍵半導體",       "category": "半導體",     "core": False},
    {"ticker": "00892.TW",  "name": "富邦台灣半導體",       "category": "半導體",     "core": False},
    {"ticker": "00713.TW",  "name": "元大台灣高息低波",     "category": "低波動",     "core": False},
    {"ticker": "00692.TW",  "name": "富邦公司治理",         "category": "治理",       "core": False},
    {"ticker": "00940.TW",  "name": "元大台灣價值高息",     "category": "價值+息",    "core": False},
    {"ticker": "00701.TW",  "name": "國泰股利精選 30",      "category": "高股息",     "core": False},
    {"ticker": "00733.TW",  "name": "富邦臺灣中小",         "category": "中小型",     "core": False},
    {"ticker": "00757.TW",  "name": "統一 FANG+",           "category": "美科技",     "core": False},
    {"ticker": "00687B.TW", "name": "國泰美債 20 年", "category": "美債（避險）", "core": False},
]

# ============================================================
# Canadian ETF universe (15 ETFs — script picks daily based on relevance)
# Always-include core: XIC, XIU, XEQT
# ============================================================
CANADA_ETFS = [
    {"ticker": "XIC.TO",  "name": "iShares S&P/TSX Capped Composite", "category": "加股大盤",   "core": True},
    {"ticker": "XIU.TO",  "name": "iShares S&P/TSX 60",               "category": "加股大型",   "core": True},
    {"ticker": "XEQT.TO", "name": "iShares Core Equity ETF Portfolio","category": "全球股票",   "core": True},
    {"ticker": "VEQT.TO", "name": "Vanguard All Equity ETF Portfolio","category": "全球股票",   "core": False},
    {"ticker": "VFV.TO",  "name": "Vanguard S&P 500 Index ETF",       "category": "美股 500",   "core": False},
    {"ticker": "ZSP.TO",  "name": "BMO S&P 500 Index ETF",            "category": "美股 500",   "core": False},
    {"ticker": "HXQ.TO",  "name": "Horizons NASDAQ-100 Index ETF",    "category": "納斯達克",   "core": False},
    {"ticker": "XUU.TO",  "name": "iShares Core S&P U.S. Total",      "category": "美股全市場", "core": False},
    {"ticker": "VCN.TO",  "name": "Vanguard FTSE Canada All Cap",     "category": "加股全市場", "core": False},
    {"ticker": "ZEB.TO",  "name": "BMO Equal Weight Banks",           "category": "加拿大銀行", "core": False},
    {"ticker": "VDY.TO",  "name": "Vanguard FTSE Cdn High Div Yield", "category": "加股高息",   "core": False},
    {"ticker": "CDZ.TO",  "name": "iShares Cdn Select Dividend",      "category": "加股股息",   "core": False},
    {"ticker": "XBAL.TO", "name": "iShares Core Balanced Portfolio",  "category": "平衡型",     "core": False},
    {"ticker": "XGRO.TO", "name": "iShares Core Growth Portfolio",    "category": "成長型",     "core": False},
    {"ticker": "HXS.TO",  "name": "Horizons S&P 500 Index ETF",       "category": "美股 500",   "core": False},
]

# ============================================================
# TSX Top 15 watchlist (mix of big caps, sectors, and dynamic movers)
# ============================================================
TSX_TOP15 = [
    {"ticker": "CLS.TO",  "name": "Celestica",             "sector": "科技/AI"},
    {"ticker": "CCO.TO",  "name": "Cameco",                "sector": "鈾礦"},
    {"ticker": "BB.TO",   "name": "BlackBerry",            "sector": "科技"},
    {"ticker": "HIVE.V",  "name": "HIVE Digital",          "sector": "加密"},
    {"ticker": "WPM.TO",  "name": "Wheaton Precious",      "sector": "貴金屬"},
    {"ticker": "MFC.TO",  "name": "Manulife Financial",    "sector": "金融"},
    {"ticker": "SU.TO",   "name": "Suncor Energy",         "sector": "能源"},
    {"ticker": "CNQ.TO",  "name": "Canadian Natural Res",  "sector": "能源"},
    {"ticker": "AEM.TO",  "name": "Agnico Eagle Mines",    "sector": "黃金"},
    {"ticker": "ENB.TO",  "name": "Enbridge",              "sector": "能源管線"},
    {"ticker": "RY.TO",   "name": "Royal Bank of Canada",  "sector": "金融"},
    {"ticker": "TD.TO",   "name": "Toronto-Dominion Bank", "sector": "金融"},
    {"ticker": "SHOP.TO", "name": "Shopify",               "sector": "科技"},
    {"ticker": "CNR.TO",  "name": "Canadian Nat Railway",  "sector": "運輸"},
    {"ticker": "BAM.TO",  "name": "Brookfield Asset Mgmt", "sector": "金融"},
]

# ============================================================
# TAIEX Top 15 watchlist
# ============================================================
TAIEX_TOP15 = [
    {"ticker": "2330.TW", "name": "台積電",       "sector": "半導體"},
    {"ticker": "2317.TW", "name": "鴻海",         "sector": "AI 伺服器"},
    {"ticker": "2454.TW", "name": "聯發科",       "sector": "IC 設計"},
    {"ticker": "2308.TW", "name": "台達電",       "sector": "電源/AI"},
    {"ticker": "2382.TW", "name": "廣達",         "sector": "伺服器"},
    {"ticker": "3231.TW", "name": "緯創",         "sector": "伺服器"},
    {"ticker": "2303.TW", "name": "聯電",         "sector": "晶圓代工"},
    {"ticker": "3036.TW", "name": "文曄",         "sector": "IC 通路"},
    {"ticker": "2344.TW", "name": "華邦電",       "sector": "記憶體"},
    {"ticker": "2891.TW", "name": "中信金",       "sector": "金融"},
    {"ticker": "2884.TW", "name": "玉山金",       "sector": "金融"},
    {"ticker": "3008.TW", "name": "大立光",       "sector": "光學"},
    {"ticker": "2603.TW", "name": "長榮海運",     "sector": "航運"},
    {"ticker": "2609.TW", "name": "陽明海運",     "sector": "航運"},
    {"ticker": "4938.TW", "name": "和碩",         "sector": "代工"},
]

# ============================================================
# Macro indicators
# ============================================================
MACRO = [
    {"ticker": "CL=F",    "name": "WTI 原油",       "unit": "USD"},
    {"ticker": "BZ=F",    "name": "Brent 原油",     "unit": "USD"},
    {"ticker": "GC=F",    "name": "黃金",           "unit": "USD"},
    {"ticker": "DX-Y.NYB","name": "美元指數 DXY",   "unit": ""},
    {"ticker": "CADUSD=X","name": "加元/美元",      "unit": ""},
    {"ticker": "BTC-USD", "name": "比特幣 BTC",     "unit": "USD"},
    {"ticker": "^VIX",    "name": "VIX 恐慌指數",   "unit": ""},
]

US_INDICES = [
    {"ticker": "^DJI",  "name": "Dow"},
    {"ticker": "^GSPC", "name": "S&P 500"},
    {"ticker": "^IXIC", "name": "Nasdaq"},
]

# ============================================================
# Index tickers
# ============================================================
TSX_INDEX_TICKER   = "^GSPTSE"
TAIEX_INDEX_TICKER = "^TWII"

# ============================================================
# Output settings
# ============================================================
USERNAME = "jobimtg"
REPO     = "daily-stock-reports"
TIMEZONE = "America/Vancouver"
