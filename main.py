from __future__ import annotations

from datetime import datetime

from config import PKT, SIGNALS_FILE
from data_fetcher import expand_watchlist, fetch_market_index, fetch_symbol_data, is_trading_day, load_watchlist
from indicators import add_indicators
from macro_sentiment import get_macro_sentiment
from paper_trader import buy, load_json, load_portfolio, mark_to_market, save_json, save_portfolio, sell
from reports import daily_report, weekly_report
from strategy import evaluate_buy, evaluate_sell
from telegram_alerts import buy_message, report_message, sell_message, send_telegram


def append_signal(signal: dict) -> None:
    """Persist signal history. / signal history محفوظ کریں۔"""
    signals = load_json(SIGNALS_FILE, [])
    signals.append(signal)
    save_json(SIGNALS_FILE, signals)


def main() -> None:
    """Run one PSX paper-trading cycle. / ایک PSX paper-trading cycle چلائیں۔"""
    now = datetime.now(PKT)
    if not is_trading_day(now):
        print(f"Skip: non-trading day {now.date()}")
        return

    watchlist = load_watchlist()
    if now.weekday() == 4:
        watchlist = expand_watchlist(watchlist)

    market_trend, index_level = fetch_market_index()
    macro = get_macro_sentiment()
    macro_score = float(macro["score"])
    portfolio = load_portfolio()
    latest_prices: dict[str, float] = {}
    data_cache = {}

    for symbol in sorted(set(watchlist) | set(portfolio["holdings"].keys())):
        df = add_indicators(fetch_symbol_data(symbol))
        if df.empty:
            continue
        data_cache[symbol] = df
        latest_prices[symbol] = float(df["close"].iloc[-1])

    portfolio = mark_to_market(portfolio, latest_prices)

    for symbol, holding in list(portfolio["holdings"].items()):
        sig = evaluate_sell(symbol, holding, data_cache.get(symbol))
        if sig["action"] == "SELL":
            trade = sell(portfolio, sig)
            if trade:
                send_telegram(sell_message(trade, float(portfolio["nav"])))
        elif "highest_price" in sig:
            holding["highest_price"] = sig["highest_price"]

    for symbol in watchlist:
        if symbol in portfolio["holdings"] or symbol not in data_cache:
            continue
        sig = evaluate_buy(symbol, data_cache[symbol], market_trend, macro_score)
        sig.update({"time": now.isoformat(), "market_trend": market_trend, "kse100": index_level, "macro": macro})
        append_signal(sig)
        if sig["action"] == "BUY":
            trade = buy(portfolio, sig)
            if trade:
                send_telegram(buy_message(trade, sig, macro_score))

    portfolio = mark_to_market(portfolio, latest_prices)
    save_portfolio(portfolio)
    report = daily_report(portfolio, macro_score)
    send_telegram(report_message(report, "PSX Daily Close Report"))

    if now.weekday() == 4:
        wr = weekly_report(portfolio)
        send_telegram(f"*PSX Weekly Summary*\nReturn: `{wr['total_return_pct']}%`\nWin rate: `{wr['win_rate']}`")

    print(f"PSX Paper Bot | Trend={market_trend} | Macro={macro_score} | NAV={portfolio['nav']} PKR")


if __name__ == "__main__":
    main()
