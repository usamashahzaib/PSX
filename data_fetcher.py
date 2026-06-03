from __future__ import annotations

import json
from datetime import datetime
from typing import Iterable

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

from config import KSE100_SYMBOLS, PKT, PSX_HOLIDAYS, WATCHLIST_CAP, WATCHLIST_FILE


def is_trading_day(now: datetime | None = None) -> bool:
    """Return True only on PSX business days. / صرف پی ایس ایکس کاروباری دن پر True دیں۔"""
    today = (now or datetime.now(PKT)).date()
    return today.weekday() < 5 and today not in PSX_HOLIDAYS


def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize vendor columns. / وینڈر کالمز کو ایک شکل دیں۔"""
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    try:
        df = df.sort_index()
    except Exception:
        pass
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    mapping = {c: c.lower().replace(" ", "_") for c in df.columns}
    df.rename(columns=mapping, inplace=True)
    aliases = {
        "open": "open", "high": "high", "low": "low", "close": "close",
        "adj_close": "close", "volume": "volume",
    }
    cols = {v: k for k, v in aliases.items() if k in df.columns}
    if "close" not in cols and "adj_close" in df.columns:
        cols["close"] = "adj_close"
    need = ["open", "high", "low", "close", "volume"]
    out = pd.DataFrame({c: pd.to_numeric(df[cols[c]], errors="coerce") for c in need if c in cols})
    return out.dropna(subset=["close"]).tail(260)


def fetch_psxdata(symbol: str) -> pd.DataFrame:
    """Try psxdata dynamic APIs. / psxdata کے ممکنہ API آزمائیں۔"""
    try:
        import psxdata  # type: ignore
    except Exception:
        return pd.DataFrame()

    candidates = [
        ("fetch", (symbol,)),
        ("get_data", (symbol,)),
        ("stocks", (symbol,)),
        ("ticker", (symbol,)),
    ]
    for name, args in candidates:
        fn = getattr(psxdata, name, None)
        if callable(fn):
            try:
                return _normalize_ohlcv(fn(*args))
            except Exception:
                continue
    return pd.DataFrame()


def fetch_yfinance(symbol: str) -> pd.DataFrame:
    """Fallback to Yahoo Finance .KA ticker. / Yahoo Finance .KA fallback استعمال کریں۔"""
    try:
        return _normalize_ohlcv(yf.download(f"{symbol}.KA", period="1y", interval="1d", progress=False))
    except Exception:
        return pd.DataFrame()


def fetch_psx_html(symbol: str) -> pd.DataFrame:
    """Final PSX HTML fallback for latest quote. / آخری PSX HTML fallback برائے تازہ quote۔"""
    url = f"https://dps.psx.com.pk/company/{symbol}"
    try:
        html = requests.get(url, timeout=15, headers={"User-Agent": "psx-paper-bot"}).text
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(soup.stripped_strings)
        nums = [float(x.replace(",", "")) for x in text.split() if x.replace(",", "").replace(".", "", 1).isdigit()]
        if not nums:
            return pd.DataFrame()
        close = nums[0]
        return pd.DataFrame([{"open": close, "high": close, "low": close, "close": close, "volume": 0.0}])
    except Exception:
        return pd.DataFrame()


def fetch_symbol_data(symbol: str) -> pd.DataFrame:
    """Fetch OHLCV using layered free sources. / مفت ذرائع سے تہہ دار OHLCV حاصل کریں۔"""
    for fetcher in (fetch_psxdata, fetch_yfinance, fetch_psx_html):
        df = fetcher(symbol)
        if not df.empty:
            return df
    return pd.DataFrame()


def fetch_market_index() -> tuple[str, float]:
    """Classify KSE-100 trend. / KSE-100 رجحان classify کریں۔"""
    try:
        df = yf.download("^KSE", period="3mo", interval="1d", progress=False)
        df = _normalize_ohlcv(df)
        if len(df) >= 20:
            close, ema20 = df["close"].iloc[-1], df["close"].ewm(span=20).mean().iloc[-1]
            trend = "Bullish" if close > ema20 * 1.01 else "Bearish" if close < ema20 * 0.99 else "Neutral"
            return trend, float(close)
    except Exception:
        pass
    return "Neutral", 0.0


def load_watchlist() -> list[str]:
    """Load persisted watchlist. / محفوظ watchlist لوڈ کریں۔"""
    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return list(dict.fromkeys(data.get("symbols", [])))[:WATCHLIST_CAP]
    except Exception:
        from config import SEED_WATCHLIST
        return SEED_WATCHLIST[:]


def save_watchlist(symbols: Iterable[str]) -> None:
    """Persist watchlist. / watchlist محفوظ کریں۔"""
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump({"symbols": list(dict.fromkeys(symbols))[:WATCHLIST_CAP]}, f, indent=2)


def expand_watchlist(current: list[str]) -> list[str]:
    """Weekly scan for liquid momentum names. / ہفتہ وار لیکوئڈ momentum names شامل کریں۔"""
    expanded = current[:]
    for symbol in KSE100_SYMBOLS:
        if symbol in expanded or len(expanded) >= WATCHLIST_CAP:
            continue
        df = fetch_symbol_data(symbol)
        if len(df) < 6:
            continue
        avg_vol = df["volume"].tail(5).mean()
        momentum = (df["close"].iloc[-1] / df["close"].iloc[-6] - 1) * 100
        if avg_vol > 500_000 and momentum > 3:
            expanded.append(symbol)
    save_watchlist(expanded)
    return expanded
