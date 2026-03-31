# 24/7 Trading Bot - Quick Setup

## What it does
- Scans top 20 S&P 500 stocks every 5 minutes during market hours
- Sends Telegram alerts when it finds signals with ≥80% confidence
- Responds to commands (`/scan`, `/analyze AAPL`, `/status`)
- Runs 24/7 in the background

## Setup (1 minute)

1. **Set your credentials:**
```cmd
set TELEGRAM_BOT_TOKEN=8556680195:AAFbhG8e4uYIHKJv7QSCQSDsyl2olXwN6n8
set TELEGRAM_CHAT_IDS=7194312099
set ANTHROPIC_API_KEY=your_anthropic_key_here
```

2. **Run the bot:**
```cmd
cd C:\Users\aravn
python TradingBot.py
```

Or just double-click `start_bot.bat`

## Telegram Commands

- `/scan` - Scan market immediately
- `/analyze AAPL` - Get analysis of a stock
- `/status` - Check if bot is running
- `/stop` - Pause auto-scanning
- `/start` - Resume auto-scanning
- `/help` - Show commands

## What You'll Get

**Automatic alerts during market hours (9:30 AM - 4 PM ET):**
```
🚨 AAPL - BUY
💰 Entry: $185.50
🛡️ Stop Loss: $183.20
🎯 Target: $189.80
📊 Confidence: 87%
📝 RSI oversold + volume surge
```

**Manual analysis anytime:**
```
/analyze TSLA
```

## Configuration

Edit these in `TradingBot.py`:
- `scan_universe` - Which stocks to scan (default: top 20 S&P 500)
- `min_confidence` - Minimum confidence to alert (default: 80%)
- `scan_interval_minutes` - How often to scan (default: 5 minutes)

## Running 24/7

To keep it running even when you close the terminal:
1. Install `pythonw` (comes with Python)
2. Run: `pythonw TradingBot.py`
3. Or use Task Scheduler to start it on boot

## Logs

Check `trading_bot.log` for scan history and errors.
