# PSX Analysis Bot

Paper-only Pakistan Stock Exchange bot. No real trading path exists.

Python `3.12` recommended. `psxdata` requires Python `>=3.11`.

## Features

- Tracks PSX symbols in PKR.
- Uses `psxdata`, Yahoo `.KA`, then PSX HTML fallback.
- Computes RSI, MACD, EMA20, volume spikes.
- Reads free RSS macro/news sentiment.
- Applies macro veto before BUY.
- Tracks active holdings, trades, NAV, P&L.
- Sends Telegram BUY/SELL/daily/weekly alerts.
- Runs via GitHub Actions at 10:30 UTC / 3:30 PM PKT.

## Local Setup

```powershell
cd C:\Users\Tier-3\Documents\PSX\psx_analysis_bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
python .\main.py
```

## Git + GitHub

```powershell
cd C:\Users\Tier-3\Documents\PSX\psx_analysis_bot
git init
git add .
git commit -m "Add PSX paper trading bot"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## GitHub Secrets

Create repository secrets:

- `PSX_TELEGRAM_BOT_TOKEN`
- `PSX_TELEGRAM_CHAT_ID`

GitHub path:

`Repo -> Settings -> Secrets and variables -> Actions -> New repository secret`

## Paper Rules

- Initial capital: `20,000 PKR`
- Max position: `5,000 PKR`
- Max holdings: `4`
- Brokerage: `0.5%`
- SECP levy: `0.1%`
- CDC: `0.01%`
- WHT on gains: `15%`
- Entry slippage: `0.2%`

## Warning

This is a research/paper-trading system only. It does not place real orders.
