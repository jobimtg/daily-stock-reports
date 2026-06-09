"""
Configuration for the daily stock report (v3 - multi-region).
The script picks the most relevant items each day from these universes.
"""

# ============================================================
# Investment Portfolio (full report only — keeps it private)
# ============================================================
PORTFOLIO = [
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

# ============================================================
# TAIEX stock universe (~40 candidates, script picks 25 daily)
# Core: always included regardless of movement.
# Non-core: filled by biggest absolute % movers each day.
# ============================================================
TAIEX_UNIVERSE = [
    # Core 權值股 (always shown)
    {"ticker": "2330.TW", "name": "台積電",   "sector": "半導體",   "core": True},
    {"ticker": "2317.TW", "name": "鴻海",     "sector": "AI 伺服器","core": True},
    {"ticker": "2454.TW", "name": "聯發科",   "sector": "IC 設計", "core": True},
    {"ticker": "2308.TW", "name": "台達電",   "sector": "電源/AI", "core": True},
    {"ticker": "2382.TW", "name": "廣達",     "sector": "伺服器",  "core": True},
    # Non-core pool
    {"ticker": "1101.TW", "name": "台泥",      "sector": "水泥",    "core": False},
    {"ticker": "1216.TW", "name": "統一",      "sector": "食品",    "core": False},
    {"ticker": "1301.TW", "name": "台塑",      "sector": "塑化",    "core": False},
    {"ticker": "1303.TW", "name": "南亞",      "sector": "塑化",    "core": False},
    {"ticker": "1326.TW", "name": "台化",      "sector": "塑化",    "core": False},
    {"ticker": "2002.TW", "name": "中鋼",      "sector": "鋼鐵",    "core": False},
    {"ticker": "2207.TW", "name": "和泰車",    "sector": "汽車",    "core": False},
    {"ticker": "2303.TW", "name": "聯電",      "sector": "晶圓代工","core": False},
    {"ticker": "2344.TW", "name": "華邦電",    "sector": "記憶體",  "core": False},
    {"ticker": "2345.TW", "name": "智邦",      "sector": "網通",    "core": False},
    {"ticker": "2357.TW", "name": "華碩",      "sector": "電子",    "core": False},
    {"ticker": "2376.TW", "name": "技嘉",      "sector": "AI 伺服器","core": False},
    {"ticker": "2379.TW", "name": "瑞昱",      "sector": "IC 設計", "core": False},
    {"ticker": "2412.TW", "name": "中華電",    "sector": "電信",    "core": False},
    {"ticker": "2603.TW", "name": "長榮海運",  "sector": "航運",    "core": False},
    {"ticker": "2609.TW", "name": "陽明海運",  "sector": "航運",    "core": False},
    {"ticker": "2615.TW", "name": "萬海",      "sector": "航運",    "core": False},
    {"ticker": "2618.TW", "name": "長榮航",    "sector": "航空",    "core": False},
    {"ticker": "2880.TW", "name": "華南金",    "sector": "金融",    "core": False},
    {"ticker": "2881.TW", "name": "富邦金",    "sector": "金融",    "core": False},
    {"ticker": "2882.TW", "name": "國泰金",    "sector": "金融",    "core": False},
    {"ticker": "2884.TW", "name": "玉山金",    "sector": "金融",    "core": False},
    {"ticker": "2886.TW", "name": "兆豐金",    "sector": "金融",    "core": False},
    {"ticker": "2887.TW", "name": "台新金",    "sector": "金融",    "core": False},
    {"ticker": "2890.TW", "name": "永豐金",    "sector": "金融",    "core": False},
    {"ticker": "2891.TW", "name": "中信金",    "sector": "金融",    "core": False},
    {"ticker": "2892.TW", "name": "第一金",    "sector": "金融",    "core": False},
    {"ticker": "2912.TW", "name": "統一超",    "sector": "通路",    "core": False},
    {"ticker": "3008.TW", "name": "大立光",    "sector": "光學",    "core": False},
    {"ticker": "3034.TW", "name": "聯詠",      "sector": "IC 設計", "core": False},
    {"ticker": "3036.TW", "name": "文曄",      "sector": "IC 通路", "core": False},
    {"ticker": "3231.TW", "name": "緯創",      "sector": "伺服器",  "core": False},
    {"ticker": "3711.TW", "name": "日月光投控","sector": "封測",    "core": False},
    {"ticker": "4904.TW", "name": "遠傳",      "sector": "電信",    "core": False},
    {"ticker": "4938.TW", "name": "和碩",      "sector": "代工",    "core": False},
    {"ticker": "5871.TW","name": "中租-KY",   "sector": "金融",    "core": False},
    {"ticker": "5880.TW", "name": "合庫金",    "sector": "金融",    "core": False},
    {"ticker": "6505.TW", "name": "台塑化",    "sector": "塑化",    "core": False},
    {"ticker": "6770.TW", "name": "力積電",    "sector": "晶圓代工","core": False},
    {"ticker": "8046.TW", "name": "南電",      "sector": "PCB",     "core": False},

]

# ============================================================
# TAIEX ETF universe (~30 candidates, script picks 25 daily)
# ============================================================
TAIEX_ETFS = [
    # Core 三大主力
    {"ticker": "0050.TW",   "name": "元大台灣 50",          "category": "大盤",       "core": True},
    {"ticker": "0056.TW",   "name": "元大高股息",           "category": "高股息",     "core": True},
    {"ticker": "00878.TW",  "name": "國泰永續高股息",       "category": "ESG 高息",   "core": True},
    # Pool
    {"ticker": "006208.TW", "name": "富邦台 50",            "category": "大盤",       "core": False},
    {"ticker": "00692.TW",  "name": "富邦公司治理",         "category": "治理",       "core": False},
    {"ticker": "00701.TW",  "name": "國泰股利精選 30",      "category": "高股息",     "core": False},
    {"ticker": "00713.TW",  "name": "元大台灣高息低波",     "category": "低波動",     "core": False},
    {"ticker": "00733.TW",  "name": "富邦臺灣中小",         "category": "中小型",     "core": False},
    {"ticker": "00757.TW",  "name": "統一 FANG+",           "category": "美科技",     "core": False},
    {"ticker": "00891.TW",  "name": "中信關鍵半導體",       "category": "半導體",     "core": False},
    {"ticker": "00892.TW",  "name": "富邦台灣半導體",       "category": "半導體",     "core": False},
    {"ticker": "00919.TW",  "name": "群益台灣精選高息",     "category": "高股息",     "core": False},
    {"ticker": "00929.TW",  "name": "復華台灣科技優息",     "category": "科技+息",    "core": False},
    {"ticker": "00940.TW",  "name": "元大台灣價值高息",     "category": "價值+息",    "core": False},
    {"ticker": "00646.TW",  "name": "元大 S&P 500",         "category": "美股",       "core": False},
    {"ticker": "00662.TW",  "name": "富邦 NASDAQ",          "category": "美股科技",   "core": False},
    {"ticker": "00770.TW",  "name": "國泰北美科技",         "category": "美股科技",   "core": False},
    {"ticker": "00830.TW",  "name": "國泰費城半導體",       "category": "美股半導體", "core": False},
    {"ticker": "00850.TW",  "name": "元大臺灣 ESG 永續",    "category": "ESG",        "core": False},
    {"ticker": "00876.TW",  "name": "元大全球 5G",          "category": "全球科技",   "core": False},
    {"ticker": "00881.TW",  "name": "國泰台灣 5G+",         "category": "5G",         "core": False},
    {"ticker": "00885.TW",  "name": "富邦越南",             "category": "越南",       "core": False},
    {"ticker": "00893.TW",  "name": "國泰智能電動車",       "category": "電動車",     "core": False},
    {"ticker": "00895.TW",  "name": "富邦未來車",           "category": "電動車",     "core": False},
    {"ticker": "00900.TW",  "name": "富邦特選高股息 30",    "category": "高股息",     "core": False},
    {"ticker": "00912.TW",  "name": "中信臺灣智慧 50",      "category": "智能選股",   "core": False},
    {"ticker": "00913.TW",  "name": "兆豐台灣晶圓製造",     "category": "半導體",     "core": False},
    {"ticker": "00935.TW",  "name": "野村臺灣新科技 50",    "category": "科技",       "core": False},
]

# ============================================================
# TSX stock universe (~25 candidates, script picks 15 daily)
# (Full report only)
# ============================================================
TSX_UNIVERSE = [
    {"ticker": "RY.TO",   "name": "Royal Bank of Canada",  "sector": "金融",     "core": True},
    {"ticker": "TD.TO",   "name": "Toronto-Dominion Bank", "sector": "金融",     "core": True},
    {"ticker": "ENB.TO",  "name": "Enbridge",              "sector": "能源管線", "core": True},
    {"ticker": "CNQ.TO",  "name": "Canadian Natural Res",  "sector": "能源",     "core": True},
    {"ticker": "SHOP.TO", "name": "Shopify",               "sector": "科技",     "core": True},
    {"ticker": "CLS.TO",  "name": "Celestica",             "sector": "科技/AI",  "core": False},
    {"ticker": "CCO.TO",  "name": "Cameco",                "sector": "鈾礦",     "core": False},
    {"ticker": "BB.TO",   "name": "BlackBerry",            "sector": "科技",     "core": False},
    {"ticker": "HIVE.V",  "name": "HIVE Digital",          "sector": "加密",     "core": False},
    {"ticker": "WPM.TO",  "name": "Wheaton Precious",      "sector": "貴金屬",   "core": False},
    {"ticker": "MFC.TO",  "name": "Manulife Financial",    "sector": "金融",     "core": False},
    {"ticker": "SU.TO",   "name": "Suncor Energy",         "sector": "能源",     "core": False},
    {"ticker": "AEM.TO",  "name": "Agnico Eagle Mines",    "sector": "黃金",     "core": False},
    {"ticker": "CNR.TO",  "name": "Canadian Nat Railway",  "sector": "運輸",     "core": False},
    {"ticker": "BAM.TO",  "name": "Brookfield Asset Mgmt", "sector": "金融",     "core": False},
    {"ticker": "BNS.TO",  "name": "Bank of Nova Scotia",   "sector": "金融",     "core": False},
    {"ticker": "BMO.TO",  "name": "Bank of Montreal",      "sector": "金融",     "core": False},
    {"ticker": "CP.TO",   "name": "Canadian Pacific",      "sector": "運輸",     "core": False},
    {"ticker": "NTR.TO",  "name": "Nutrien",               "sector": "農業",     "core": False},
    {"ticker": "SLF.TO",  "name": "Sun Life Financial",    "sector": "金融",     "core": False},
    {"ticker": "TRP.TO",  "name": "TC Energy",             "sector": "能源管線", "core": False},
    {"ticker": "WCN.TO",  "name": "Waste Connections",     "sector": "工業",     "core": False},
    {"ticker": "L.TO",    "name": "Loblaw Companies",      "sector": "通路",     "core": False},
    {"ticker": "DOL.TO",  "name": "Dollarama",             "sector": "通路",     "core": False},
    {"ticker": "ABX.TO",  "name": "Barrick Gold",          "sector": "黃金",     "core": False},
]

# ============================================================
# Canadian ETF universe (~20 candidates, script picks 15 daily)
# (Full report only)
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
    {"ticker": "XIT.TO",  "name": "iShares S&P/TSX Capped IT",        "category": "加股科技",   "core": False},
    {"ticker": "ZAG.TO",  "name": "BMO Aggregate Bond Index",         "category": "加幣債券",   "core": False},
    {"ticker": "ZQQ.TO",  "name": "BMO NASDAQ 100 Index Hedged",      "category": "納斯達克",   "core": False},
    {"ticker": "VAB.TO",  "name": "Vanguard Cdn Aggregate Bond",      "category": "加幣債券",   "core": False},
    {"ticker": "XSP.TO",  "name": "iShares S&P 500 (CAD Hedged)",     "category": "美股 500",   "core": False},
]

# ============================================================
# Macro indicators
# ============================================================
MACRO = [
    {"ticker": "CL=F",     "name": "WTI 原油",       "unit": "USD"},
    {"ticker": "BZ=F",     "name": "Brent 原油",     "unit": "USD"},
    {"ticker": "GC=F",     "name": "黃金",           "unit": "USD"},
    {"ticker": "DX-Y.NYB", "name": "美元指數 DXY",   "unit": ""},
    {"ticker": "CADUSD=X", "name": "加元/美元",      "unit": ""},
    {"ticker": "TWDUSD=X", "name": "台幣/美元",      "unit": ""},
    {"ticker": "BTC-USD",  "name": "比特幣 BTC",     "unit": "USD"},
    {"ticker": "^VIX",     "name": "VIX 恐慌指數",   "unit": ""},
]

US_INDICES = [
    {"ticker": "^DJI",  "name": "Dow"},
    {"ticker": "^GSPC", "name": "S&P 500"},
    {"ticker": "^IXIC", "name": "Nasdaq"},
]

TSX_INDEX_TICKER   = "^GSPTSE"
TAIEX_INDEX_TICKER = "^TWII"

# ============================================================
# Region configuration
# ============================================================
USERNAME = "jobimtg"
REPO     = "daily-stock-reports"

# Per-region settings: timezone, sections to include, output paths, file naming
REGIONS = {
    "full": {
        "timezone":      "America/Vancouver",
        "city":          "Vancouver, BC",
        "filename_fmt":  "daily-financial-brief-{date}.html",
        "summary_path":  "canada/latest.json",
        "output_subdir": "canada",
        "url_path_fmt":  "canada/daily-financial-brief-{date}.html",
        "show_sections": ["tsx", "taiex", "etf_tw", "etf_ca",
                          "top_tsx", "top_taiex", "macro",
                          "conclusion", "portfolio", "sources"],
        "top_taiex_n":   25,
        "etf_taiex_n":   25,
        "top_tsx_n":     15,
        "etf_ca_n":      15,
    },
    "tw": {
        "timezone":      "Asia/Taipei",
        "city":          "Taipei, TW",
        "filename_fmt":  "daily-tw-brief-{date}.html",
        "summary_path":  "taiwan/latest.json",
        "output_subdir": "taiwan",
        "url_path_fmt":  "taiwan/daily-tw-brief-{date}.html",
        "show_sections": ["taiex", "etf_tw", "top_taiex",
                          "macro", "conclusion", "sources"],
        "top_taiex_n":   25,
        "etf_taiex_n":   25,
    },
}
