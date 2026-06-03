from __future__ import annotations

from datetime import datetime

from config import DAILY_REPORT_FILE, INITIAL_CAPITAL_PKR, PKT, TRADES_FILE, WEEKLY_REPORT_FILE
from paper_trader import load_json, save_json


def daily_report(portfolio: dict, macro_score: float) -> dict:
    """Generate daily report JSON. / daily report JSON بنائیں۔"""
    holdings_value = sum(float(h.get("current_value", 0)) for h in portfolio["holdings"].values())
    report = {
        "time": datetime.now(PKT).isoformat(),
        "cash": round(float(portfolio["cash"]), 2),
        "holdings_value": round(holdings_value, 2),
        "nav": round(float(portfolio["nav"]), 2),
        "total_pnl": round(float(portfolio["nav"]) - INITIAL_CAPITAL_PKR, 2),
        "macro_score": macro_score,
        "holdings": portfolio["holdings"],
    }
    save_json(DAILY_REPORT_FILE, report)
    return report


def weekly_report(portfolio: dict) -> dict:
    """Generate Friday weekly report. / جمعہ weekly report بنائیں۔"""
    trades = load_json(TRADES_FILE, [])
    sells = [t for t in trades if t.get("side") == "SELL"]
    wins = [t for t in sells if float(t.get("realized_pnl", 0)) > 0]
    best = max(sells, key=lambda t: t.get("realized_pnl", 0), default={})
    worst = min(sells, key=lambda t: t.get("realized_pnl", 0), default={})
    report = {
        "time": datetime.now(PKT).isoformat(),
        "total_return_pct": round((float(portfolio["nav"]) / INITIAL_CAPITAL_PKR - 1) * 100, 2),
        "best_trade": best,
        "worst_trade": worst,
        "win_rate": round(len(wins) / len(sells), 3) if sells else 0.0,
        "current_holdings": portfolio["holdings"],
    }
    save_json(WEEKLY_REPORT_FILE, report)
    return report
