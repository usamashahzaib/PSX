from __future__ import annotations

import pandas as pd

from config import MACRO_BUY_LIMIT, MACRO_BUY_VETO


def rsi_thresholds(market_trend: str) -> tuple[float, float]:
    """Dynamic RSI thresholds by regime. / regime کے مطابق RSI thresholds۔"""
    return (35, 70) if market_trend == "Bullish" else (40, 75) if market_trend == "Bearish" else (37, 72)


def evaluate_buy(symbol: str, df: pd.DataFrame, market_trend: str, macro_score: float) -> dict:
    """Confluence BUY engine. / confluence BUY engine۔"""
    if len(df) < 30:
        return {"symbol": symbol, "action": "HOLD", "reason": "Insufficient data / data کم ہے"}
    if macro_score < MACRO_BUY_VETO:
        return {"symbol": symbol, "action": "HOLD", "reason": f"Macro veto {macro_score} / macro veto"}

    row = df.iloc[-1]
    oversold, _ = rsi_thresholds(market_trend)
    reclaim_ema = row["close"] >= row["ema20"] or df["close"].iloc[-2] < df["ema20"].iloc[-2] <= row["close"]
    checks = {
        "RSI oversold": row["rsi14"] < oversold,
        "MACD bullish crossover": bool(row["macd_bull_cross"]),
        "Price above/reclaiming EMA20": bool(reclaim_ema),
        "Volume spike": bool(row["volume_spike"]),
        "KSE trend not bearish": market_trend in {"Bullish", "Neutral"},
        "Macro acceptable": macro_score >= MACRO_BUY_LIMIT,
    }
    return {
        "symbol": symbol,
        "action": "BUY" if all(checks.values()) else "HOLD",
        "price": float(row["close"]),
        "rsi": round(float(row["rsi14"]), 2),
        "checks": checks,
        "reason": "; ".join(k for k, v in checks.items() if v) or "No confluence / confluence نہیں",
    }


def evaluate_sell(symbol: str, holding: dict, df: pd.DataFrame | None) -> dict:
    """TP/SL/reversal SELL engine. / TP/SL/reversal SELL engine۔"""
    if df is None or df.empty:
        return {"symbol": symbol, "action": "HOLD", "reason": "No data / data نہیں"}
    row = df.iloc[-1]
    price = float(row["close"])
    high = max(float(holding.get("highest_price", price)), price)
    entry = float(holding["entry_price"])
    overbought = row["rsi14"] > 72
    reversal = bool(overbought and row["macd_bear_cross"])
    if price >= entry * 1.08:
        reason = "Take profit +8% / منافع +8%"
    elif price <= high * 0.96:
        reason = "Trailing stop -4% / trailing stop -4%"
    elif reversal:
        reason = "RSI overbought + MACD bearish / RSI overbought + MACD bearish"
    else:
        return {"symbol": symbol, "action": "HOLD", "highest_price": high, "price": price}
    return {"symbol": symbol, "action": "SELL", "price": price, "highest_price": high, "reason": reason}
