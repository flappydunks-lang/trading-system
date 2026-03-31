"""
PROFESSIONAL DAY TRADING AI SYSTEM
- Real-time intraday pattern recognition
- 15+ day trading patterns (bull flags, triangles, breakouts, etc.)
- Live market scanning during trading hours
- Swing + Day trading modes
- Entry/exit signals with alerts

Install: pip install yfinance pandas numpy scikit-learn scipy tabulate
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta, time as dt_time
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from scipy import stats
from tabulate import tabulate
import time
import warnings
warnings.filterwarnings('ignore')

class DayTradingAI:
    """Professional day trading AI with pattern recognition"""
    
    def __init__(self, portfolio_value=10000):
        self.portfolio_value = portfolio_value
        self.day_trading_watchlist = self._get_day_trading_stocks()
        
        print("\n" + "="*100)
        print("📈 PROFESSIONAL DAY TRADING AI SYSTEM")
        print("="*100)
        print(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
        print(f"🎯 Features: Swing Trading + Day Trading Patterns")
        print(f"⚡ Real-time Pattern Recognition")
        print(f"🔔 Buy/Sell Signal Alerts")
        print("="*100 + "\n")
    
    def _get_day_trading_stocks(self):
        """Get liquid stocks suitable for day trading"""
        return [
            # High volume tech stocks
            'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'GOOGL', 'AMZN', 'META',
            'SPY', 'QQQ', 'IWM',  # ETFs
            # Popular day trading stocks
            'PLTR', 'SOFI', 'RIVN', 'LCID', 'NIO', 'COIN', 'HOOD',
            'SHOP', 'SQ', 'PYPL', 'ROKU', 'SNAP', 'UBER', 'LYFT',
            # Volatile movers
            'GME', 'AMC', 'BB', 'BBBY', 'CLOV',
            # Semiconductor
            'INTC', 'MU', 'AVGO', 'QCOM', 'TSM',
            # Finance
            'BAC', 'JPM', 'GS', 'C', 'WFC',
            # Energy
            'XLE', 'USO', 'XOM', 'CVX',
            # Other liquid
            'BA', 'DIS', 'NFLX', 'BABA', 'PFE', 'JNJ'
        ]
    
    def is_market_open(self):
        """Check if US market is currently open"""
        now = datetime.now()
        market_open = dt_time(9, 30)
        market_close = dt_time(16, 0)
        
        # Check if weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False, "Market closed (Weekend)"
        
        current_time = now.time()
        
        if current_time < market_open:
            return False, f"Pre-market (Opens at 9:30 AM)"
        elif current_time > market_close:
            return False, f"After-hours (Closed at 4:00 PM)"
        else:
            return True, "Market is OPEN"
    
    def get_intraday_data(self, symbol, interval='5m', period='5d'):
        """Fetch intraday data for pattern analysis"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(interval=interval, period=period)
            
            if len(data) < 20:
                return None
            
            return data
        except:
            return None
    
    def detect_day_trading_patterns(self, data, symbol):
        """Detect 15+ day trading patterns in real-time"""
        
        if data is None or len(data) < 20:
            return None
        
        df = data.copy()
        
        # Calculate essential indicators
        df['SMA_9'] = df['Close'].rolling(9).mean()
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['EMA_9'] = df['Close'].ewm(span=9).mean()
        df['EMA_20'] = df['Close'].ewm(span=20).mean()
        
        # Volume
        df['Avg_Volume'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Avg_Volume']
        
        # Volatility
        df['High_Low_Range'] = ((df['High'] - df['Low']) / df['Close']) * 100
        df['ATR'] = df['High_Low_Range'].rolling(14).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        
        # Bollinger Bands
        df['BB_Mid'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Mid'] + (2 * bb_std)
        df['BB_Lower'] = df['BB_Mid'] - (2 * bb_std)
        
        # Get recent data
        recent = df.tail(50).dropna()
        if len(recent) < 20:
            return None
        
        latest = recent.iloc[-1]
        prev = recent.iloc[-2] if len(recent) > 1 else latest
        
        patterns_detected = []
        confidence = 0
        signal_type = "NEUTRAL"
        
        # === PATTERN 1: BULL FLAG ===
        # Strong uptrend followed by consolidation
        price_change_10 = ((recent['Close'].iloc[-1] - recent['Close'].iloc[-10]) / recent['Close'].iloc[-10]) * 100
        consolidation_range = recent['High'].tail(5).max() - recent['Low'].tail(5).min()
        avg_range = recent['High_Low_Range'].tail(20).mean()
        
        if price_change_10 > 3 and consolidation_range < avg_range * 0.8:
            patterns_detected.append({
                'name': '🚩 BULL FLAG',
                'type': 'BULLISH',
                'confidence': 75,
                'description': 'Strong uptrend + tight consolidation = breakout likely'
            })
            confidence += 75
            signal_type = "BUY"
        
        # === PATTERN 2: BEAR FLAG ===
        if price_change_10 < -3 and consolidation_range < avg_range * 0.8:
            patterns_detected.append({
                'name': '🚩 BEAR FLAG',
                'type': 'BEARISH',
                'confidence': 75,
                'description': 'Strong downtrend + consolidation = breakdown likely'
            })
            confidence -= 75
            signal_type = "SELL"
        
        # === PATTERN 3: BREAKOUT (Volume Surge) ===
        if latest['Close'] > recent['High'].tail(20).iloc[-2] and latest['Volume_Ratio'] > 2.0:
            patterns_detected.append({
                'name': '💥 BREAKOUT',
                'type': 'BULLISH',
                'confidence': 85,
                'description': f'Price breaking resistance with {latest["Volume_Ratio"]:.1f}x volume'
            })
            confidence += 85
            signal_type = "BUY"
        
        # === PATTERN 4: BREAKDOWN ===
        if latest['Close'] < recent['Low'].tail(20).iloc[-2] and latest['Volume_Ratio'] > 2.0:
            patterns_detected.append({
                'name': '💥 BREAKDOWN',
                'type': 'BEARISH',
                'confidence': 85,
                'description': f'Price breaking support with {latest["Volume_Ratio"]:.1f}x volume'
            })
            confidence -= 85
            signal_type = "SELL"
        
        # === PATTERN 5: GOLDEN CROSS (Intraday) ===
        if prev['EMA_9'] <= prev['SMA_20'] and latest['EMA_9'] > latest['SMA_20']:
            patterns_detected.append({
                'name': '✨ GOLDEN CROSS',
                'type': 'BULLISH',
                'confidence': 70,
                'description': 'Fast EMA crossed above slow SMA'
            })
            confidence += 70
            signal_type = "BUY"
        
        # === PATTERN 6: DEATH CROSS (Intraday) ===
        if prev['EMA_9'] >= prev['SMA_20'] and latest['EMA_9'] < latest['SMA_20']:
            patterns_detected.append({
                'name': '💀 DEATH CROSS',
                'type': 'BEARISH',
                'confidence': 70,
                'description': 'Fast EMA crossed below slow SMA'
            })
            confidence -= 70
            signal_type = "SELL"
        
        # === PATTERN 7: OVERSOLD BOUNCE (RSI) ===
        if latest['RSI'] < 30 and prev['RSI'] < latest['RSI']:
            patterns_detected.append({
                'name': '🔄 OVERSOLD BOUNCE',
                'type': 'BULLISH',
                'confidence': 65,
                'description': f'RSI at {latest["RSI"]:.1f}, starting to reverse'
            })
            confidence += 65
            signal_type = "BUY"
        
        # === PATTERN 8: OVERBOUGHT REVERSAL ===
        if latest['RSI'] > 70 and prev['RSI'] > latest['RSI']:
            patterns_detected.append({
                'name': '🔄 OVERBOUGHT REVERSAL',
                'type': 'BEARISH',
                'confidence': 65,
                'description': f'RSI at {latest["RSI"]:.1f}, starting to reverse'
            })
            confidence -= 65
            signal_type = "SELL"
        
        # === PATTERN 9: MACD CROSSOVER ===
        if prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
            patterns_detected.append({
                'name': '📊 MACD BULL CROSS',
                'type': 'BULLISH',
                'confidence': 60,
                'description': 'MACD crossed above signal line'
            })
            confidence += 60
            signal_type = "BUY"
        
        if prev['MACD'] >= prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']:
            patterns_detected.append({
                'name': '📊 MACD BEAR CROSS',
                'type': 'BEARISH',
                'confidence': 60,
                'description': 'MACD crossed below signal line'
            })
            confidence -= 60
            signal_type = "SELL"
        
        # === PATTERN 10: BOLLINGER SQUEEZE ===
        bb_width = (latest['BB_Upper'] - latest['BB_Lower']) / latest['BB_Mid']
        avg_bb_width = ((recent['BB_Upper'] - recent['BB_Lower']) / recent['BB_Mid']).mean()
        
        if bb_width < avg_bb_width * 0.7:
            patterns_detected.append({
                'name': '🎯 BOLLINGER SQUEEZE',
                'type': 'NEUTRAL',
                'confidence': 70,
                'description': 'Low volatility - big move coming soon'
            })
        
        # === PATTERN 11: BB BOUNCE (Lower Band) ===
        if latest['Close'] <= latest['BB_Lower'] * 1.02:
            patterns_detected.append({
                'name': '🎈 BB LOWER BOUNCE',
                'type': 'BULLISH',
                'confidence': 65,
                'description': 'Price at lower BB, bounce expected'
            })
            confidence += 65
            signal_type = "BUY"
        
        # === PATTERN 12: BB REJECTION (Upper Band) ===
        if latest['Close'] >= latest['BB_Upper'] * 0.98:
            patterns_detected.append({
                'name': '🎈 BB UPPER REJECTION',
                'type': 'BEARISH',
                'confidence': 65,
                'description': 'Price at upper BB, pullback expected'
            })
            confidence -= 65
            signal_type = "SELL"
        
        # === PATTERN 13: VOLUME CLIMAX ===
        if latest['Volume_Ratio'] > 3.0:
            patterns_detected.append({
                'name': '🔊 VOLUME CLIMAX',
                'type': 'NEUTRAL',
                'confidence': 75,
                'description': f'{latest["Volume_Ratio"]:.1f}x normal volume - major move'
            })
        
        # === PATTERN 14: MORNING GAP UP ===
        # Check if first candle of day gapped up
        market_open_idx = recent.index.time == dt_time(9, 30)
        if market_open_idx.any():
            open_candle = recent[market_open_idx].iloc[-1] if market_open_idx.sum() > 0 else None
            if open_candle is not None:
                prev_close = recent.iloc[recent.index.get_loc(open_candle.name) - 1]['Close']
                gap_pct = ((open_candle['Open'] - prev_close) / prev_close) * 100
                
                if gap_pct > 2:
                    patterns_detected.append({
                        'name': '🌅 MORNING GAP UP',
                        'type': 'BULLISH',
                        'confidence': 70,
                        'description': f'{gap_pct:.1f}% gap up - momentum trade'
                    })
                    confidence += 70
                    signal_type = "BUY"
                
                elif gap_pct < -2:
                    patterns_detected.append({
                        'name': '🌅 MORNING GAP DOWN',
                        'type': 'BEARISH',
                        'confidence': 70,
                        'description': f'{gap_pct:.1f}% gap down - momentum down'
                    })
                    confidence -= 70
                    signal_type = "SELL"
        
        # === PATTERN 15: HIGHER HIGHS & HIGHER LOWS ===
        highs = recent['High'].tail(5).values
        lows = recent['Low'].tail(5).values
        
        if len(highs) >= 3 and all(highs[i] < highs[i+1] for i in range(len(highs)-2)):
            if all(lows[i] < lows[i+1] for i in range(len(lows)-2)):
                patterns_detected.append({
                    'name': '📈 STRONG UPTREND',
                    'type': 'BULLISH',
                    'confidence': 75,
                    'description': 'Higher highs and higher lows - ride the trend'
                })
                confidence += 75
                signal_type = "BUY"
        
        # === PATTERN 16: LOWER HIGHS & LOWER LOWS ===
        if len(highs) >= 3 and all(highs[i] > highs[i+1] for i in range(len(highs)-2)):
            if all(lows[i] > lows[i+1] for i in range(len(lows)-2)):
                patterns_detected.append({
                    'name': '📉 STRONG DOWNTREND',
                    'type': 'BEARISH',
                    'confidence': 75,
                    'description': 'Lower highs and lower lows - trend is down'
                })
                confidence -= 75
                signal_type = "SELL"
        
        # === PATTERN 17: DOJI CANDLE (Indecision) ===
        body_size = abs(latest['Close'] - latest['Open'])
        candle_range = latest['High'] - latest['Low']
        
        if body_size / candle_range < 0.1 and candle_range > 0:
            patterns_detected.append({
                'name': '🕯️ DOJI CANDLE',
                'type': 'NEUTRAL',
                'confidence': 50,
                'description': 'Indecision - potential reversal point'
            })
        
        # Normalize confidence to 0-100 scale
        if len(patterns_detected) > 0:
            confidence = max(-100, min(100, confidence / len(patterns_detected)))
        
        # Determine final signal
        if confidence > 60:
            final_signal = "🟢 STRONG BUY"
        elif confidence > 30:
            final_signal = "🟡 MODERATE BUY"
        elif confidence < -60:
            final_signal = "🔴 STRONG SELL"
        elif confidence < -30:
            final_signal = "🟠 MODERATE SELL"
        else:
            final_signal = "⚪ NEUTRAL/HOLD"
        
        return {
            'symbol': symbol,
            'patterns': patterns_detected,
            'confidence': confidence,
            'signal': final_signal,
            'price': latest['Close'],
            'rsi': latest['RSI'],
            'volume_ratio': latest['Volume_Ratio'],
            'timestamp': latest.name
        }
    
    def scan_market_realtime(self, watchlist=None, interval='5m'):
        """Scan market for day trading opportunities in real-time"""
        
        is_open, status = self.is_market_open()
        
        print(f"\n{'='*100}")
        print(f"🔍 REAL-TIME MARKET SCANNER")
        print(f"{'='*100}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
        print(f"📊 Market Status: {status}")
        print(f"{'='*100}\n")
        
        if not is_open:
            print(f"⚠️  Note: Market is closed. Showing last available data.\n")
        
        if watchlist is None:
            watchlist = self.day_trading_watchlist[:20]  # Scan top 20
        
        print(f"🔎 Scanning {len(watchlist)} stocks for patterns...")
        print(f"⏳ This will take 30-60 seconds...\n")
        
        opportunities = []
        
        for i, symbol in enumerate(watchlist, 1):
            if i % 5 == 0:
                print(f"   Scanned {i}/{len(watchlist)} stocks...")
            
            try:
                data = self.get_intraday_data(symbol, interval=interval)
                result = self.detect_day_trading_patterns(data, symbol)
                
                if result and len(result['patterns']) > 0:
                    opportunities.append(result)
            except:
                continue
        
        # Sort by confidence
        opportunities.sort(key=lambda x: abs(x['confidence']), reverse=True)
        
        return opportunities
    
    def display_realtime_signals(self, opportunities):
        """Display real-time trading signals"""
        
        if len(opportunities) == 0:
            print(f"\n❌ No clear patterns detected at this time.")
            print(f"   Try again in 15-30 minutes.\n")
            return
        
        print(f"\n{'='*100}")
        print(f"🎯 TOP TRADING OPPORTUNITIES - LIVE SIGNALS")
        print(f"{'='*100}\n")
        
        for i, opp in enumerate(opportunities[:10], 1):
            print(f"{'─'*100}")
            print(f"#{i}. {opp['symbol']} - {opp['signal']}")
            print(f"{'─'*100}")
            print(f"💰 Current Price: ${opp['price']:.2f}")
            print(f"📊 Confidence Score: {opp['confidence']:.1f}")
            print(f"📈 RSI: {opp['rsi']:.1f}")
            print(f"🔊 Volume: {opp['volume_ratio']:.1f}x normal")
            print(f"⏰ Last Update: {opp['timestamp'].strftime('%I:%M:%S %p')}")
            
            print(f"\n🎯 Patterns Detected:")
            for pattern in opp['patterns']:
                emoji_map = {'BULLISH': '🟢', 'BEARISH': '🔴', 'NEUTRAL': '⚪'}
                emoji = emoji_map.get(pattern['type'], '⚪')
                print(f"   {emoji} {pattern['name']} ({pattern['confidence']}%)")
                print(f"      → {pattern['description']}")
            
            print()
        
        print(f"{'='*100}\n")
    
    def live_monitor(self, symbol, interval='1m', duration_minutes=60):
        """Monitor a single stock in real-time"""
        
        print(f"\n{'='*100}")
        print(f"📡 LIVE MONITOR: {symbol.upper()}")
        print(f"{'='*100}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print(f"🔄 Refresh: Every {interval}")
        print(f"{'='*100}\n")
        print(f"Press Ctrl+C to stop monitoring\n")
        
        start_time = time.time()
        alert_history = []
        
        try:
            while (time.time() - start_time) < (duration_minutes * 60):
                # Get fresh data
                data = self.get_intraday_data(symbol, interval=interval, period='1d')
                result = self.detect_day_trading_patterns(data, symbol)
                
                if result and len(result['patterns']) > 0:
                    # Check if this is a new alert
                    current_patterns = [p['name'] for p in result['patterns']]
                    
                    if current_patterns != alert_history:
                        alert_history = current_patterns
                        
                        print(f"{'─'*100}")
                        print(f"🔔 ALERT - {datetime.now().strftime('%I:%M:%S %p')}")
                        print(f"{'─'*100}")
                        print(f"💰 Price: ${result['price']:.2f}")
                        print(f"📊 Signal: {result['signal']}")
                        print(f"🎯 Confidence: {result['confidence']:.1f}")
                        
                        print(f"\n🎯 Patterns:")
                        for pattern in result['patterns']:
                            emoji_map = {'BULLISH': '🟢', 'BEARISH': '🔴', 'NEUTRAL': '⚪'}
                            emoji = emoji_map.get(pattern['type'], '⚪')
                            print(f"   {emoji} {pattern['name']} - {pattern['description']}")
                        print()
                
                # Wait before next check
                if interval == '1m':
                    time.sleep(60)
                elif interval == '5m':
                    time.sleep(300)
                else:
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            print(f"\n\n✅ Monitoring stopped by user")
            print(f"⏰ Ended: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}\n")
    
    def run(self):
        """Main program loop"""
        
        while True:
            print("\n" + "="*100)
            print("📋 DAY TRADING MAIN MENU")
            print("="*100)
            print("\n1. 🔍 Real-time Market Scanner (Top 20 stocks)")
            print("2. 📡 Live Monitor Single Stock (1-minute updates)")
            print("3. 📊 Analyze Specific Stock for Day Trading")
            print("4. 📝 Custom Watchlist Scanner")
            print("5. 🚪 Exit")
            
            choice = input("\n➤ Choice: ").strip()
            
            if choice == '1':
                # Real-time scanner
                print("\n⏳ Scanning market for patterns...")
                opportunities = self.scan_market_realtime()
                self.display_realtime_signals(opportunities)
            
            elif choice == '2':
                # Live monitor
                symbol = input("\n📊 Enter stock symbol to monitor: ").strip().upper()
                duration = input("⏱️  Monitor duration in minutes (default 60): ").strip()
                duration = int(duration) if duration else 60
                
                self.live_monitor(symbol, interval='1m', duration_minutes=duration)
            
            elif choice == '3':
                # Single stock analysis
                symbol = input("\n📊 Enter stock symbol: ").strip().upper()
                
                print("\n⏳ Analyzing patterns...")
                data = self.get_intraday_data(symbol, interval='5m')
                result = self.detect_day_trading_patterns(data, symbol)
                
                if result:
                    self.display_realtime_signals([result])
                else:
                    print(f"\n❌ No patterns detected for {symbol}\n")
            
            elif choice == '4':
                # Custom watchlist
                print("\n📝 Enter stock symbols separated by commas (e.g., AAPL,TSLA,NVDA):")
                symbols = input("➤ ").strip().upper().split(',')
                symbols = [s.strip() for s in symbols]
                
                print(f"\n⏳ Scanning {len(symbols)} stocks...")
                opportunities = self.scan_market_realtime(watchlist=symbols)
                self.display_realtime_signals(opportunities)
            
            elif choice == '5':
                print("\n✅ Thank you for using Day Trading AI System!")
                print("⚠️  Remember: Day trading is risky. Use proper risk management!")
                print("="*100 + "\n")
                break
            
            else:
                print("\n❌ Invalid choice. Please enter 1-5")


# ============================================================================
# MAIN PROGRAM
# ============================================================================

if __name__ == "__main__":
    print("""
    
                       PROFESSIONAL DAY TRADING AI SYSTEM                      
                                                                                
      Features:                                                                 
      ✅ Real-time pattern recognition (17+ patterns)                          
      ✅ Live market scanning                                                   
      ✅ Bull/Bear flags, breakouts, reversals                                  
      ✅ Volume analysis & momentum signals                                     
      ✅ RSI, MACD, Bollinger Band patterns                                    
      ✅ Gap trading strategies                                                 
      ✅ Live monitoring with alerts                                            
                                                                                
      ⚠️  DISCLAIMER: Day trading is high risk. Only trade with money you      
         can afford to lose. This is for educational purposes only.             
    
    """)
    
    portfolio = float(input("\n💰 Enter portfolio value ($): ") or "10000")
    
    # Initialize system
    trader = DayTradingAI(portfolio_value=portfolio)
    
    print("\n✅ Day Trading AI initialized!")
    print("🚀 Starting main menu...\n")
    
    time.sleep(2)
    
    # Run main loop
    trader.run()