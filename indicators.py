from __future__ import annotations

import numpy as np
import pandas as pd

from config import VOLUME_SPIKE_MULTIPLIER


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """RSI with pandas/numpy only. / صرف pandas/numpy سے RSI۔"""
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """MACD 12/26/9. / MACD 12/26/9۔"""
    fast = series.ewm(span=12, adjust=False).mean()
    slow = series.ewm(span=26, adjust=False).mean()
    line = fast - slow
    signal = line.ewm(span=9, adjust=False).mean()
    return line, signal


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Attach technical indicators. / تکنیکی indicators شامل کریں۔"""
    if df is None or df.empty or "close" not in df.columns:
        return pd.DataFrame()
    out = df.copy()
    out["ema20"] = out["close"].ewm(span=20, adjust=False).mean()
    out["rsi14"] = rsi(out["close"], 14)
    out["macd"], out["macd_signal"] = macd(out["close"])
    out["avg_vol10"] = out["volume"].rolling(10).mean()
    out["volume_spike"] = out["volume"] > out["avg_vol10"] * VOLUME_SPIKE_MULTIPLIER
    out["macd_bull_cross"] = (out["macd"] > out["macd_signal"]) & (out["macd"].shift(1) <= out["macd_signal"].shift(1))
    out["macd_bear_cross"] = (out["macd"] < out["macd_signal"]) & (out["macd"].shift(1) >= out["macd_signal"].shift(1))
    return out
