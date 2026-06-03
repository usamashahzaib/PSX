from __future__ import annotations

import json
import os
from datetime import datetime

import numpy as np

from config import (
    BROKERAGE_RATE, CDC_RATE, INITIAL_CAPITAL_PKR, MAX_HOLDINGS, MAX_POSITION_PKR,
    PKT, PORTFOLIO_FILE, SECP_LEVY_RATE, SLIPPAGE_RATE, TRADES_FILE,
    WHT_CAPITAL_GAIN_RATE,
)


def _blank_portfolio() -> dict:
    """Initial portfolio state. / ابتدائی portfolio state۔"""
    return {"cash": INITIAL_CAPITAL_PKR, "holdings": {}, "realized_pnl": 0.0, "nav": INITIAL_CAPITAL_PKR}


def load_json(path: str, default):
    """Safe JSON loader. / محفوظ JSON loader۔"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: str, data) -> None:
    """Atomic-enough JSON save. / JSON محفوظ کریں۔"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=_json_default)


def _json_default(value):
    """Convert NumPy/Pandas scalars for JSON. / NumPy/Pandas scalars کو JSON بنائیں۔"""
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def load_portfolio() -> dict:
    """Load persisted portfolio. / محفوظ portfolio لوڈ کریں۔"""
    return load_json(PORTFOLIO_FILE, _blank_portfolio())


def save_portfolio(portfolio: dict) -> None:
    """Persist portfolio after every run. / ہر run کے بعد portfolio محفوظ کریں۔"""
    save_json(PORTFOLIO_FILE, portfolio)


def _append_trade(trade: dict) -> None:
    """Append trade history. / trade history شامل کریں۔"""
    trades = load_json(TRADES_FILE, [])
    trades.append(trade)
    save_json(TRADES_FILE, trades)


def buy(portfolio: dict, signal: dict) -> dict | None:
    """Simulate paper BUY only. / صرف paper BUY simulate کریں۔"""
    symbol, raw_price = signal["symbol"], float(signal["price"])
    if symbol in portfolio["holdings"] or len(portfolio["holdings"]) >= MAX_HOLDINGS:
        return None
    spend = min(MAX_POSITION_PKR, float(portfolio["cash"]))
    exec_price = raw_price * (1 + SLIPPAGE_RATE)
    fees = spend * (BROKERAGE_RATE + SECP_LEVY_RATE + CDC_RATE)
    qty = max(0, int((spend - fees) // exec_price))
    if qty <= 0:
        return None
    cost = qty * exec_price + fees
    portfolio["cash"] -= cost
    portfolio["holdings"][symbol] = {
        "entry_price": round(exec_price, 4),
        "quantity": qty,
        "capital": round(cost, 2),
        "highest_price": round(exec_price, 4),
        "entry_time": datetime.now(PKT).isoformat(),
    }
    trade = {"time": datetime.now(PKT).isoformat(), "side": "BUY", "symbol": symbol, "price": exec_price, "qty": qty, "fees": fees}
    _append_trade(trade)
    return trade


def sell(portfolio: dict, signal: dict) -> dict | None:
    """Simulate paper SELL only. / صرف paper SELL simulate کریں۔"""
    symbol = signal["symbol"]
    holding = portfolio["holdings"].get(symbol)
    if not holding:
        return None
    qty, exit_price = int(holding["quantity"]), float(signal["price"])
    gross = qty * exit_price
    fees = gross * (BROKERAGE_RATE + SECP_LEVY_RATE + CDC_RATE)
    gain = gross - fees - float(holding["capital"])
    wht = max(0.0, gain) * WHT_CAPITAL_GAIN_RATE
    net = gross - fees - wht
    realized = net - float(holding["capital"])
    portfolio["cash"] += net
    portfolio["realized_pnl"] = float(portfolio.get("realized_pnl", 0)) + realized
    del portfolio["holdings"][symbol]
    trade = {
        "time": datetime.now(PKT).isoformat(), "side": "SELL", "symbol": symbol,
        "price": exit_price, "qty": qty, "fees": fees, "wht": wht,
        "realized_pnl": round(realized, 2), "reason": signal["reason"],
    }
    _append_trade(trade)
    return trade


def mark_to_market(portfolio: dict, prices: dict[str, float]) -> dict:
    """Update NAV and unrealized P&L. / NAV اور unrealized P&L اپڈیٹ کریں۔"""
    holdings_value = 0.0
    for symbol, h in portfolio["holdings"].items():
        price = float(prices.get(symbol, h["entry_price"]))
        h["current_price"] = round(price, 4)
        h["highest_price"] = round(max(float(h.get("highest_price", price)), price), 4)
        h["current_value"] = round(price * int(h["quantity"]), 2)
        h["unrealized_pnl"] = round(h["current_value"] - float(h["capital"]), 2)
        holdings_value += h["current_value"]
    portfolio["nav"] = round(float(portfolio["cash"]) + holdings_value, 2)
    return portfolio
