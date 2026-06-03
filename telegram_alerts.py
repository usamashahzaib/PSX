from __future__ import annotations

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram(message: str) -> bool:
    """Send Markdown Telegram alert if secrets exist. / secrets ہوں تو Markdown alert بھیجیں۔"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=15)
        return r.ok
    except Exception:
        return False


def buy_message(trade: dict, signal: dict, macro_score: float) -> str:
    """Build BUY message. / BUY پیغام بنائیں۔"""
    price = float(trade["price"])
    return (
        f"*PSX PAPER BUY*\n"
        f"Stock: `{trade['symbol']}`\nEntry: `{price:.2f} PKR`\nQty: `{trade['qty']}`\n"
        f"Capital: `{price * trade['qty']:.2f} PKR`\nTarget: `{price * 1.08:.2f}`\nStop: `{price * 0.96:.2f}`\n"
        f"Reasons: `{signal.get('reason', '')}`\nMacro: `{macro_score}`"
    )


def sell_message(trade: dict, nav: float) -> str:
    """Build SELL message. / SELL پیغام بنائیں۔"""
    return (
        f"*PSX PAPER SELL*\nStock: `{trade['symbol']}`\nExit: `{trade['price']:.2f} PKR`\n"
        f"P&L: `{trade['realized_pnl']:.2f} PKR`\nReason: `{trade['reason']}`\nNAV: `{nav:.2f} PKR`"
    )


def report_message(report: dict, title: str) -> str:
    """Build report message. / report پیغام بنائیں۔"""
    return (
        f"*{title}*\nCash: `{report['cash']:.2f} PKR`\nHoldings: `{report['holdings_value']:.2f} PKR`\n"
        f"NAV: `{report['nav']:.2f} PKR`\nP&L: `{report['total_pnl']:.2f} PKR`\nMacro: `{report['macro_score']}`"
    )
