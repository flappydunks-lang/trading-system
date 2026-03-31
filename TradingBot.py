#!/usr/bin/env python3
"""
24/7 Trading Alert Bot - Telegram Edition
Scans market continuously and sends alerts via Telegram
"""

import os
import sys
import time
import logging
from datetime import datetime, time as dtime
from pathlib import Path
import threading
import json

# Import the main trading system
from Trading import (
    AIAnalyzer, TechnicalAnalyzer, DataManager, MarketScanner,
    MARKET_UNIVERSES, TradingConfig, TradingStyle
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot with command handlers."""
    
    def __init__(self, token: str, chat_ids: list):
        self.token = token
        self.chat_ids = chat_ids
        self.last_update_id = 0
        
    def send_message(self, text: str, parse_mode: str = "HTML"):
        """Send message to all chat IDs."""
        import requests
        for chat_id in self.chat_ids:
            try:
                url = f"https://api.telegram.org/bot{self.token}/sendMessage"
                requests.post(url, json={
                    "chat_id": chat_id,
                    "text": text[:4000],
                    "parse_mode": parse_mode
                }, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
    
    def get_updates(self):
        """Get new messages."""
        import requests
        try:
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 10}
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            if data.get("ok"):
                return data.get("result", [])
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
        return []
    
    def handle_command(self, message: str, scanner) -> str:
        """Handle bot commands."""
        cmd = message.strip().lower()
        
        if cmd == "/start" or cmd == "/help":
            return (
                "🤖 <b>Trading Bot Commands</b>\n\n"
                "/scan - Scan market now\n"
                "/status - Check scanner status\n"
                "/analyze TICKER - Analyze a stock\n"
                "/stop - Stop auto-scanning\n"
                "/start - Resume auto-scanning"
            )
        
        elif cmd == "/status":
            status = "🟢 Running" if scanner.running else "🔴 Stopped"
            return f"Scanner: {status}\nLast scan: {scanner.last_scan_time}"
        
        elif cmd == "/scan":
            scanner.manual_scan = True
            return "🔍 Manual scan triggered..."
        
        elif cmd.startswith("/analyze "):
            ticker = cmd.split()[1].upper() if len(cmd.split()) > 1 else ""
            if ticker:
                return f"Analyzing {ticker}... (results will be sent shortly)"
            return "Usage: /analyze TICKER"
        
        elif cmd == "/stop":
            scanner.running = False
            return "⏸️ Auto-scanning paused. Use /start to resume."
        
        else:
            return "Unknown command. Use /help for available commands."


class MarketScanner24x7:
    """24/7 market scanner with Telegram alerts."""
    
    def __init__(self, api_key: str, bot: TelegramBot, config: dict):
        self.api_key = api_key
        self.bot = bot
        self.config = config
        self.running = True
        self.manual_scan = False
        self.last_scan_time = "Never"
        
        # Initialize analyzers
        try:
            self.analyzer = AIAnalyzer(api_key)
            self.technical = TechnicalAnalyzer()
        except Exception as e:
            self.analyzer = None
            logger.error(f"Failed to initialize AI analyzer: {e}")
        
        logger.info("Scanner initialized")
    
    def is_market_hours(self) -> bool:
        """Check if US market is open."""
        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo("America/New_York"))
        except:
            now = datetime.now()
        
        # Weekend check
        if now.weekday() >= 5:
            return False
        
        # Market hours: 9:30 AM - 4:00 PM ET
        market_open = dtime(9, 30)
        market_close = dtime(16, 0)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
    
    def scan_market(self):
        """Scan market for opportunities."""
        logger.info("Starting market scan...")
        self.last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check saved option positions first
        self.check_option_positions()
        
        # Use configured universe or default to top 50
        universe = self.config.get('scan_universe', MARKET_UNIVERSES['sp500_top50'][:20])
        min_confidence = self.config.get('min_confidence', 80)
        
        opportunities = []
        
        for ticker in universe:
            try:
                # Fetch data
                df = DataManager.fetch_data(ticker, "5d", "15m")
                if df is None or len(df) < 50:
                    continue
                
                # Calculate indicators
                indicators = self.technical.calculate_indicators(df)
                if not indicators:
                    continue
                
                # Use fallback analysis if AI not available
                if self.analyzer:
                    try:
                        analysis = self.analyzer._fallback_analysis(
                            ticker, indicators, 
                            self.config.get('account_size', 10000),
                            0.02,
                            self.config.get('default_rrr', 2.0)
                        )
                    except:
                        continue
                else:
                    continue
                
                # Check confidence threshold
                if analysis.confidence >= min_confidence and analysis.action in ['BUY', 'SELL']:
                    opportunities.append({
                        'ticker': ticker,
                        'action': analysis.action,
                        'confidence': analysis.confidence,
                        'price': analysis.entry_price,
                        'sl': analysis.stop_loss,
                        'tp': analysis.take_profit_1,
                        'reason': analysis.primary_reason
                    })
                    
            except Exception as e:
                logger.error(f"Error scanning {ticker}: {e}")
                continue
        
        # Send alerts for high-confidence opportunities
        if opportunities:
            opportunities.sort(key=lambda x: x['confidence'], reverse=True)
            for opp in opportunities[:5]:  # Top 5
                alert = (
                    f"🚨 <b>{opp['ticker']}</b> - {opp['action']}\n"
                    f"💰 Entry: ${opp['price']:.2f}\n"
                    f"🛡️ Stop Loss: ${opp['sl']:.2f}\n"
                    f"🎯 Target: ${opp['tp']:.2f}\n"
                    f"📊 Confidence: {opp['confidence']:.0f}%\n"
                    f"📝 {opp['reason']}"
                )
                self.bot.send_message(alert)
                time.sleep(1)  # Rate limit
        
        logger.info(f"Scan complete. Found {len(opportunities)} opportunities.")
    
    def check_option_positions(self):
        """Monitor saved option positions and send exit alerts."""
        import json
        from pathlib import Path
        
        position_file = Path('results/options_positions.json')
        if not position_file.exists():
            return
        
        try:
            with open(position_file, 'r') as f:
                positions = json.load(f)
        except:
            return
        
        # Filter only open positions
        open_positions = [p for p in positions if p.get('status') == 'OPEN']
        if not open_positions:
            return
        
        logger.info(f"Checking {len(open_positions)} open option positions...")
        
        updated = False
        for pos in open_positions:
            try:
                underlying = pos['underlying']
                opt_type = pos['type']
                strike = pos['strike']
                expiration = pos['expiration']
                entry_premium = pos['entry_premium']
                stop_premium = pos['stop_premium']
                target_premium = pos['target_premium']
                contracts = pos['contracts']
                
                # Fetch current premium
                import yfinance as yf
                opt = yf.Ticker(underlying)
                chain = opt.option_chain(expiration)
                table = chain.calls if opt_type == 'CALL' else chain.puts
                
                if not table.empty:
                    row = table.iloc[(table['strike'] - strike).abs().argsort()[:1]]
                    ask = float(row['ask'].values[0]) if hasattr(row['ask'].values[0], '__float__') else None
                    bid = float(row['bid'].values[0]) if hasattr(row['bid'].values[0], '__float__') else None
                    
                    if ask and bid and ask > 0 and bid > 0:
                        current_premium = (ask + bid) / 2
                    elif ask and ask > 0:
                        current_premium = ask
                    elif bid and bid > 0:
                        current_premium = bid
                    else:
                        continue
                    
                    # Check exit conditions
                    pnl_per_contract = (current_premium - entry_premium) * 100
                    total_pnl = pnl_per_contract * contracts
                    
                    # Hit target
                    if current_premium >= target_premium:
                        alert = (
                            f"🎯 <b>TARGET HIT!</b>\n"
                            f"{underlying} {opt_type} ${strike} exp {expiration}\n"
                            f"Current: ${current_premium:.2f} (Target: ${target_premium:.2f})\n"
                            f"P&L: ${total_pnl:,.2f} ({contracts} contracts)\n"
                            f"<b>🟢 SELL TO CLOSE</b>"
                        )
                        self.bot.send_message(alert)
                        pos['status'] = 'CLOSED_TARGET'
                        pos['exit_premium'] = current_premium
                        pos['exit_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        updated = True
                    
                    # Hit stop
                    elif current_premium <= stop_premium:
                        alert = (
                            f"🛑 <b>STOP LOSS HIT</b>\n"
                            f"{underlying} {opt_type} ${strike} exp {expiration}\n"
                            f"Current: ${current_premium:.2f} (Stop: ${stop_premium:.2f})\n"
                            f"P&L: ${total_pnl:,.2f} ({contracts} contracts)\n"
                            f"<b>🔴 SELL TO CLOSE</b>"
                        )
                        self.bot.send_message(alert)
                        pos['status'] = 'CLOSED_STOP'
                        pos['exit_premium'] = current_premium
                        pos['exit_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        updated = True
                    
                    # Check if expiration approaching (within 2 days)
                    elif (datetime.strptime(expiration, "%Y-%m-%d") - datetime.now()).days <= 2:
                        if total_pnl > 0:
                            alert = (
                                f"⏰ <b>EXPIRATION ALERT</b>\n"
                                f"{underlying} {opt_type} ${strike} expires in {(datetime.strptime(expiration, '%Y-%m-%d') - datetime.now()).days} days\n"
                                f"Current: ${current_premium:.2f}\n"
                                f"P&L: ${total_pnl:,.2f} (profitable)\n"
                                f"<b>Consider closing</b>"
                            )
                            self.bot.send_message(alert)
                
            except Exception as e:
                logger.error(f"Error checking position {pos.get('underlying')}: {e}")
                continue
        
        # Save updated positions
        if updated:
            try:
                with open(position_file, 'w') as f:
                    json.dump(positions, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving positions: {e}")
    
    def run(self):
        """Main scanner loop."""
        logger.info("Starting 24/7 scanner...")
        self.bot.send_message("🤖 Trading bot started! Scanning during market hours.")
        
        scan_interval = self.config.get('scan_interval_minutes', 5) * 60
        
        while True:
            try:
                # Check for manual scan trigger
                if self.manual_scan:
                    self.manual_scan = False
                    self.scan_market()
                    continue
                
                # Auto-scan during market hours
                if self.running and self.is_market_hours():
                    self.scan_market()
                    time.sleep(scan_interval)
                else:
                    # Outside market hours, just wait
                    time.sleep(60)
                    
            except KeyboardInterrupt:
                logger.info("Scanner stopped by user")
                self.bot.send_message("🛑 Trading bot stopped.")
                break
            except Exception as e:
                logger.error(f"Scanner error: {e}")
                time.sleep(60)


def start_command_listener(bot: TelegramBot, scanner: MarketScanner24x7):
    """Listen for Telegram commands in background thread."""
    logger.info("Command listener started")
    
    while scanner.running:
        try:
            updates = bot.get_updates()
            for update in updates:
                bot.last_update_id = update.get("update_id", 0)
                message = update.get("message", {})
                text = message.get("text", "")
                
                if text.startswith("/"):
                    response = bot.handle_command(text, scanner)
                    bot.send_message(response)
                    
                    # Handle analyze command
                    if text.startswith("/analyze "):
                        ticker = text.split()[1].upper() if len(text.split()) > 1 else ""
                        if ticker:
                            try:
                                df = DataManager.fetch_data(ticker, "5d", "15m")
                                if df is not None:
                                    indicators = scanner.technical.calculate_indicators(df)
                                    if indicators:
                                        analysis = scanner.analyzer._fallback_analysis(
                                            ticker, indicators, 10000, 0.02, 2.0
                                        )
                                        result = (
                                            f"📊 <b>{ticker}</b>\n"
                                            f"Action: {analysis.action}\n"
                                            f"Confidence: {analysis.confidence:.0f}%\n"
                                            f"Entry: ${analysis.entry_price:.2f}\n"
                                            f"SL: ${analysis.stop_loss:.2f}\n"
                                            f"TP: ${analysis.take_profit_1:.2f}"
                                        )
                                        bot.send_message(result)
                            except Exception as e:
                                bot.send_message(f"Error analyzing {ticker}: {str(e)}")
            
            time.sleep(2)
        except Exception as e:
            logger.error(f"Command listener error: {e}")
            time.sleep(5)


def main():
    """Main entry point."""
    
    # Load config
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_ids = os.getenv('TELEGRAM_CHAT_IDS', '').split(',')
    chat_ids = [c.strip() for c in chat_ids if c.strip()]
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not bot_token or not chat_ids:
        print("ERROR: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_IDS environment variables")
        sys.exit(1)
    
    if not api_key:
        print("WARNING: ANTHROPIC_API_KEY not set. Using fallback analysis only.")
    
    # Configuration
    config = {
        'scan_universe': MARKET_UNIVERSES['sp500_top50'][:20],  # Top 20 stocks
        'min_confidence': 80,
        'scan_interval_minutes': 5,
        'account_size': 10000,
        'default_rrr': 2.0
    }
    
    # Initialize bot and scanner
    bot = TelegramBot(bot_token, chat_ids)
    scanner = MarketScanner24x7(api_key, bot, config)
    
    # Start command listener in background
    listener_thread = threading.Thread(target=start_command_listener, args=(bot, scanner), daemon=True)
    listener_thread.start()
    
    # Run scanner
    scanner.run()


if __name__ == "__main__":
    main()
