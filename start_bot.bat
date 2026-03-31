@echo off
REM 24/7 Trading Bot Startup Script

echo ========================================
echo Starting 24/7 Trading Alert Bot
echo ========================================
echo.

REM Check environment variables
if not defined TELEGRAM_BOT_TOKEN (
    echo ERROR: TELEGRAM_BOT_TOKEN not set
    echo Set it with: set TELEGRAM_BOT_TOKEN=your_token_here
    pause
    exit /b 1
)

if not defined TELEGRAM_CHAT_IDS (
    echo ERROR: TELEGRAM_CHAT_IDS not set
    echo Set it with: set TELEGRAM_CHAT_IDS=your_chat_id_here
    pause
    exit /b 1
)

if not defined ANTHROPIC_API_KEY (
    echo WARNING: ANTHROPIC_API_KEY not set
    echo Bot will use fallback analysis only
    echo.
)

echo Configuration:
echo - Bot Token: %TELEGRAM_BOT_TOKEN:~0,20%...
echo - Chat IDs: %TELEGRAM_CHAT_IDS%
echo - Scan Interval: 5 minutes
echo - Min Confidence: 80%%
echo.

echo Starting bot...
python TradingBot.py

pause
