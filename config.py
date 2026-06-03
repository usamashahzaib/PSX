from __future__ import annotations

import os
from datetime import date, time
from zoneinfo import ZoneInfo


# Core paper account settings. / بنیادی پیپر اکاؤنٹ سیٹنگز۔
INITIAL_CAPITAL_PKR = 20_000.0
MAX_POSITION_PKR = 5_000.0
MAX_HOLDINGS = 4

# PSX market settings. / پی ایس ایکس مارکیٹ سیٹنگز۔
PKT = ZoneInfo("Asia/Karachi")
TRADING_START = time(9, 15)
TRADING_END = time(15, 30)
CIRCUIT_BREAKER_PCT = 7.5
SETTLEMENT_DAYS = 2

# Costs used by the simulator. / سمیولیٹر میں استعمال ہونے والی لاگت۔
BROKERAGE_RATE = 0.005
SECP_LEVY_RATE = 0.001
CDC_RATE = 0.0001
WHT_CAPITAL_GAIN_RATE = 0.15
SLIPPAGE_RATE = 0.002

# Strategy settings. / حکمت عملی کی سیٹنگز۔
TAKE_PROFIT_PCT = 0.08
TRAILING_STOP_PCT = 0.04
VOLUME_SPIKE_MULTIPLIER = 1.5
MACRO_BUY_VETO = -0.3
MACRO_BUY_LIMIT = -0.1
WATCHLIST_CAP = 25

# Seed liquid KSE-100 blue chips. / ابتدائی لیکوئڈ کے ایس ای 100 اسٹاکس۔
SEED_WATCHLIST = [
    "ENGRO", "OGDC", "PPL", "LUCK", "HUBC", "PSO", "MCB", "UBL", "HBL",
    "SYS", "EFERT", "UNITY", "TGL", "MLCF", "CHCC",
]

# Best-effort KSE-100 universe for weekly expansion. / ہفتہ وار توسیع کے لیے محتاط فہرست۔
KSE100_SYMBOLS = sorted(set(SEED_WATCHLIST + [
    "AICL", "AKBL", "ATRL", "BAFL", "BAHL", "BOP", "CNERGY", "DGKC", "DOL",
    "FFC", "FFL", "GHPL", "GLAXO", "HASCOL", "HCAR", "IBFL", "ILP", "INDU",
    "ISL", "KAPCO", "KEL", "KOHC", "KTML", "MARI", "MEBL", "NBP", "NML",
    "PAEL", "PIBTL", "PKGS", "POL", "PTC", "SAZEW", "SEARL", "SNGP", "SNBL",
    "SSGC", "TRG", "WTL",
]))

# Static holiday list; update annually. / جامد تعطیلات؛ ہر سال اپڈیٹ کریں۔
PSX_HOLIDAYS = {
    date(2026, 2, 5),
    date(2026, 3, 23),
    date(2026, 5, 1),
    date(2026, 8, 14),
    date(2026, 9, 6),
    date(2026, 9, 11),
    date(2026, 11, 9),
    date(2026, 12, 25),
}

# File paths. / فائل راستے۔
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(BASE_DIR, "history")
LOG_DIR = os.path.join(BASE_DIR, "logs")
PORTFOLIO_FILE = os.path.join(BASE_DIR, "portfolio.json")
TRADES_FILE = os.path.join(HISTORY_DIR, "trades.json")
SIGNALS_FILE = os.path.join(HISTORY_DIR, "signals.json")
DAILY_REPORT_FILE = os.path.join(HISTORY_DIR, "daily_report.json")
WEEKLY_REPORT_FILE = os.path.join(HISTORY_DIR, "weekly_report.json")
WATCHLIST_FILE = os.path.join(HISTORY_DIR, "watchlist.json")

# Telegram secrets from GitHub Actions or local env. / ٹیلیگرام سیکرٹس ماحول سے۔
TELEGRAM_BOT_TOKEN = os.getenv("PSX_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("PSX_TELEGRAM_CHAT_ID", "")
