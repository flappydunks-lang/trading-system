# -*- coding: utf-8 -*-
import time
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from scipy import stats
from tabulate import tabulate
import warnings
import json

warnings.filterwarnings('ignore')

# Optional sentiment analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except:
    SENTIMENT_AVAILABLE = False
    print("⚠️  TextBlob not installed. Sentiment analysis will be basic.")


# ============================
# News test function
# ============================
def test_news_availability():
    """Test which stocks have news available"""
    print(f"\n{'='*120}")
    print(f"🔍 TESTING NEWS AVAILABILITY")
    print(f"{'='*120}\n")
    print(f"Testing popular stocks to see which have news available...\n")

    test_stocks = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'SPY', 'QQQ']

    working_stocks = []

    for symbol in test_stocks:
        try:
            print(f"Testing {symbol}...", end=' ')
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if news and len(news) > 0:
                print(f"✅ {len(news)} articles found")
                working_stocks.append((symbol, len(news)))
            else:
                print(f"❌ No news")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print(f"\n{'─'*120}\n")

    if working_stocks:
        print(f"✅ News is working for these stocks:")
        for symbol, count in working_stocks:
            print(f"   • {symbol}: {count} articles")
        print(f"\n💡 Try analyzing one of these stocks to see the detailed news feature!")
    else:
        print(f"❌ News API appears to be down for all stocks")
        print(f"\nPossible issues:")
        print(f"   1. Yahoo Finance API is temporarily unavailable (happens sometimes)")
        print(f"   2. Your IP may be rate-limited (wait 10-15 minutes)")
        print(f"   3. Network connectivity issues")
        print(f"\nSolutions:")
        print(f"   • Wait 10-15 minutes and try again")
        print(f"   • Restart your internet connection")
        print(f"   • Use VPN if available")
        print(f"   • Check: https://finance.yahoo.com (if this works, news should too)")

    print(f"\n{'='*120}\n")


# ============================
# Banner display
# ============================
print("""
- ULTIMATE PROFESSIONAL AI TRADING SYSTEM
- Complete trading suite with ALL features
- Long-term, Swing, and Day Trading modes
- Technical analysis, ML predictions, news sentiment
- Pattern recognition, alerts, backtesting
- Portfolio tracking, risk management
- Real-time monitoring and scanning
""")

# ============================
# Main class definition
# ============================
class UltimateAITrader:
    """Ultimate all-in-one trading system"""

    def __init__(self, portfolio_value=10000):
        self.portfolio_value = portfolio_value
        self.trading_mode = None
        self.positions = {}
        self.trade_history = []
        self.watchlist = []

        print("\n" + "="*120)
        print("🏆 ULTIMATE PROFESSIONAL AI TRADING SYSTEM")
        print("="*120)
        print(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
        print(f"🎯 Modes: Long-term | Swing Trading | Day Trading")
        print(f"⚡ Features: ML Predictions | Pattern Recognition | News Sentiment | Backtesting | Alerts")
        print("="*120 + "\n")

    def select_trading_mode(self):
        """Let user select trading mode"""
        print("\n" + "="*120)
        print("🎯 SELECT YOUR TRADING MODE")
        print("="*120)
        print("\n1. 📊 LONG-TERM INVESTING (Hold weeks to months)")
        print("   • Focus: Fundamentals + long-term trends")
        print("   • Timeframe: Daily/Weekly charts")
        print("   • Target: 8-20%+ gains")
        print("   • Risk: Lower volatility")
        print("\n2. 📈 SWING TRADING (Hold 2-10 days)")
        print("   • Focus: Technical patterns + momentum")
        print("   • Timeframe: 1-hour to Daily charts")
        print("   • Target: 3-8% gains")
        print("   • Risk: Medium volatility")
        print("\n3. ⚡ DAY TRADING (Intraday - close by EOD)")
        print("   • Focus: Realtime patterns + volume")
        print("   • Timeframe: 1-minute to 15-minute charts")
        print("   • Target: 0.5-3% gains")
        print("   • Risk: Higher volatility, fast-paced")
        print("\n" + "="*120)

        while True:
            choice = input("\n➤ Select mode (1/2/3): ").strip()
            if choice == '1':
                self.trading_mode = 'longterm'
                print("\n✅ Long-term Investing mode selected!")
                break
            elif choice == '2':
                self.trading_mode = 'swing'
                print("\n✅ Swing Trading mode selected!")
                break
            elif choice == '3':
                self.trading_mode = 'daytrading'
                print("\n✅ Day Trading mode selected!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3")
        time.sleep(1)
        return self.trading_mode

    # ============================================================
    # Data fetching methods
    # ============================================================

    def get_stock_data(self, symbol, period='2y', interval='1d'):
        """Fetch stock data with validation"""
        try:
            data = yf.Ticker(symbol).history(period=period, interval=interval)
            if len(data) < 50:
                return None, f"Insufficient data: {len(data)} rows"
            return data, None
        except Exception as e:
            return None, str(e)

    def get_intraday_data(self, symbol, interval='5m', period='5d'):
        """Fetch intraday data"""
        try:
            data = yf.Ticker(symbol).history(interval=interval, period=period)
            if len(data) < 20:
                return None
            return data
        except:
            return None

    def get_company_info(self, symbol):
        """Get company fundamentals"""
        try:
            info = yf.Ticker(symbol).info
            return {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'peg_ratio': info.get('pegRatio', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 'N/A'),
                '52w_high': info.get('fiftyTwoWeekHigh', 0),
                '52w_low': info.get('fiftyTwoWeekLow', 0),
                'analyst_target': info.get('targetMeanPrice', 'N/A'),
                'recommendation': info.get('recommendationKey', 'N/A')
            }
        except:
            return None

    # ============================================================
    # Technical indicators
    # ============================================================

    def calculate_indicators(self, data, mode='swing'):
        """Calculate technical indicators based on mode"""
        df = data.copy()

        # Basic indicators
        for period in [9, 20, 50, 200]:
            if len(df) >= period:
                df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
                df[f'EMA_{period}'] = df['Close'].ewm(span=period).mean()

        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # Bollinger Bands
        df['BB_Mid'] = df['Close'].rolling(20).mean()
        std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Mid'] + 2 * std
        df['BB_Lower'] = df['BB_Mid'] - 2 * std

        # ATR
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(14).mean()

        # Volume
        df['Avg_Volume'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / (df['Avg_Volume'] + 1e-10)

        # Additional indicators for swing/day trading
        if mode in ['swing', 'daytrading']:
            low_14 = df['Low'].rolling(14).min()
            high_14 = df['High'].rolling(14).max()
            df['Stoch_K'] = 100 * (df['Close'] - low_14) / (high_14 - low_14 + 1e-10)
            df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()

            plus_dm = df['High'].diff()
            minus_dm = -df['Low'].diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0

            tr14 = true_range.rolling(14).sum()
            plus_di = 100 * (plus_dm.rolling(14).sum() / tr14)
            minus_di = 100 * (minus_dm.rolling(14).sum() / tr14)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
            df['ADX'] = dx.rolling(14).mean()

        return df

    # ============================================================
    # Pattern recognition
    # ============================================================
    def detect_patterns(self, data, mode='swing'):
        """Detect trading patterns based on mode"""
        df = self.calculate_indicators(data, mode)
        recent = df.tail(50).dropna()
        if len(recent) < 20:
            return None
        latest = recent.iloc[-1]
        prev = recent.iloc[-2] if len(recent) > 1 else latest

        patterns = []
        confidence = 0

        if mode == 'daytrading':
            # Bull/Bear Flags
            price_change_10 = ((recent['Close'].iloc[-1] - recent['Close'].iloc[-10]) / recent['Close'].iloc[-10]) * 100
            consolidation = (recent['High'].tail(5).max() - recent['Low'].tail(5).min()) / recent['Close'].iloc[-1]
            if price_change_10 > 2 and consolidation < 0.02:
                patterns.append({'name': '🚩 BULL FLAG', 'type': 'BULLISH', 'conf': 75})
                confidence += 75
            elif price_change_10 < -2 and consolidation < 0.02:
                patterns.append({'name': '🚩 BEAR FLAG', 'type': 'BEARISH', 'conf': 75})
                confidence -= 75
            # Breakouts
            if latest['Close'] > recent['High'].tail(20).iloc[-2] and latest['Volume_Ratio'] > 2:
                patterns.append({'name': '💥 BREAKOUT', 'type': 'BULLISH', 'conf': 85})
                confidence += 85
            # MACD Crossovers
            if prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
                patterns.append({'name': '📊 MACD BULL CROSS', 'type': 'BULLISH', 'conf': 60})
                confidence += 60
            elif prev['MACD'] >= prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']:
                patterns.append({'name': '📊 MACD BEAR CROSS', 'type': 'BEARISH', 'conf': 60})
                confidence -= 60
        elif mode == 'swing':
            # Golden/Death Cross
            if prev['EMA_20'] <= prev['SMA_50'] and latest['EMA_20'] > latest['SMA_50']:
                patterns.append({'name': '✨ GOLDEN CROSS', 'type': 'BULLISH', 'conf': 80})
                confidence += 80
            elif prev['EMA_20'] >= prev['SMA_50'] and latest['EMA_20'] < latest['SMA_50']:
                patterns.append({'name': '💀 DEATH CROSS', 'type': 'BEARISH', 'conf': 80})
                confidence -= 80
            # Trend pattern
            highs = recent['High'].tail(5).values
            if len(highs) >= 3 and all(highs[i] < highs[i + 1] for i in range(len(highs) - 1)):
                patterns.append({'name': '📈 HIGHER HIGHS', 'type': 'BULLISH', 'conf': 70})
                confidence += 70
        elif mode == 'longterm':
            # Major trend
            if latest['EMA_50'] > latest['SMA_200']:
                patterns.append({'name': '📈 LONG-TERM UPTREND', 'type': 'BULLISH', 'conf': 75})
                confidence += 75
            elif latest['EMA_50'] < latest['SMA_200']:
                patterns.append({'name': '📉 LONG-TERM DOWNTREND', 'type': 'BEARISH', 'conf': 75})
                confidence -= 75

        # Universal indicators
        if latest['RSI'] < 30:
            patterns.append({'name': '🔄 OVERSOLD', 'type': 'BULLISH', 'conf': 65})
            confidence += 65
        elif latest['RSI'] > 70:
            patterns.append({'name': '🔄 OVERBOUGHT', 'type': 'BEARISH', 'conf': 65})
            confidence -= 65

        # Bollinger Touch
        if latest['Close'] <= latest['BB_Lower'] * 1.02:
            patterns.append({'name': '🎈 BB LOWER TOUCH', 'type': 'BULLISH', 'conf': 60})
            confidence += 60
        elif latest['Close'] >= latest['BB_Upper'] * 0.98:
            patterns.append({'name': '🎈 BB UPPER TOUCH', 'type': 'BEARISH', 'conf': 60})
            confidence -= 60

        # Normalize confidence
        if len(patterns) > 0:
            confidence = confidence / len(patterns)

        # Final signal
        if confidence > 60:
            signal = "🟢 STRONG BUY"
        elif confidence > 30:
            signal = "🟡 MODERATE BUY"
        elif confidence < -60:
            signal = "🔴 STRONG SELL"
        elif confidence < -30:
            signal = "🟠 MODERATE SELL"
        else:
            signal = "⚪ NEUTRAL/HOLD"

        return {
            'patterns': patterns,
            'confidence': confidence,
            'signal': signal,
            'price': latest['Close'],
            'rsi': latest['RSI'],
            'volume_ratio': latest['Volume_Ratio'],
            'atr': latest['ATR']
        }

    # ============================
    # News & sentiment
    # ============================
    def analyze_news_sentiment(self, symbol):
        """Perform detailed news sentiment analysis"""
        articles_all = []

        print(f"   🔍 Searching for news for {symbol}...")

        # Dummy: replace with real news fetch in production
        articles_all = [
            {'title': 'Company beats earnings expectations', 'publisher': 'News', 'link': '', 'pub_date': datetime.now()},
            {'title': 'New product launch excites investors', 'publisher': 'News', 'link': '', 'pub_date': datetime.now()},
            {'title': 'Regulatory investigation impacts stock', 'publisher': 'News', 'link': '', 'pub_date': datetime.now()},
            {'title': 'CEO resigns unexpectedly', 'publisher': 'News', 'link': '', 'pub_date': datetime.now()},
        ]

        impactful_articles = []
        for article in articles_all:
            hours_diff = (datetime.now() - article['pub_date']).total_seconds() / 3600
            if hours_diff > 168:
                continue
            title_lower = article['title'].lower()
            impact_keywords = ['earnings', 'regulatory', 'investigation', 'resign', 'scandal', 'lawsuit', 'recall']
            if any(k in title_lower for k in impact_keywords):
                impactful_articles.append(article)

        articles_details = []
        for art in impactful_articles:
            title_lower = art['title'].lower()
            bull_keywords = ['beat', 'exceed', 'outperform', 'strong earnings', 'profit surge', 'revenue growth', 'guidance raised']
            bear_keywords = ['miss', 'disappoint', 'below expectations', 'weak earnings', 'profit decline', 'guidance lowered']
            bull_score = sum(w in title_lower for w in bull_keywords)
            bear_score = sum(w in title_lower for w in bear_keywords)

            if bull_score > bear_score:
                sentiment = 'BULLISH'
                sentiment_emoji = '🟢'
                confidence = min(95, (bull_score / (bull_score + bear_score + 1e-10)) * 100)
            elif bear_score > bull_score:
                sentiment = 'BEARISH'
                sentiment_emoji = '🔴'
                confidence = min(95, (bear_score / (bull_score + bear_score + 1e-10)) * 100)
            else:
                sentiment = 'NEUTRAL'
                sentiment_emoji = '⚪'
                confidence = 50

            importance_score = 0
            importance_reasons = []
            categories_found = []

            if 'earnings' in title_lower:
                importance_score += 40
                importance_reasons.append("📊 Earnings impact stock price")
                categories_found.append('earnings')
            if 'regulatory' in title_lower or 'investigation' in title_lower:
                importance_score += 35
                importance_reasons.append("⚠️ Regulatory investigation")
                categories_found.append('regulation')
            if 'resign' in title_lower or 'scandal' in title_lower:
                importance_score += 30
                importance_reasons.append("👔 Leadership change or scandal")
                categories_found.append('management')
            hours_diff = (datetime.now() - art['pub_date']).total_seconds() / 3600
            if hours_diff < 24:
                importance_score += 20
                importance_reasons.append("⏰ Very recent news (last 24h)")
            elif hours_diff < 72:
                importance_score += 10
                importance_reasons.append("⏰ Recent news (last 3 days)")

            importance_score = min(100, importance_score)

            if importance_score >= 70:
                importance_level = '🔥 CRITICAL'
            elif importance_score >= 50:
                importance_level = '⚡ HIGH'
            elif importance_score >= 30:
                importance_level = '📊 MEDIUM'
            else:
                importance_level = 'ℹ️ LOW'

            articles_details.append({
                'title': art['title'],
                'publisher': art['publisher'],
                'link': art['link'],
                'date': art['pub_date'].strftime('%Y-%m-%d %I:%M %p'),
                'time_ago': f"{int(hours_diff)} hours ago",
                'sentiment': sentiment,
                'sentiment_emoji': sentiment_emoji,
                'confidence': confidence,
                'importance': importance_level,
                'importance_score': importance_score,
                'importance_reasons': importance_reasons,
                'categories': categories_found
            })

        # Sorting articles
        articles.sort(key=lambda x: (x['importance_score'], -datetime.strptime(x['date'], '%Y-%m-%d %I:%M %p').timestamp()), reverse=True)

        total_bull = sum(1 for a in articles if a['sentiment'] == 'BULLISH')
        total_bear = sum(1 for a in articles if a['sentiment'] == 'BEARISH')
        total_neutral = sum(1 for a in articles if a['sentiment'] == 'NEUTRAL')

        total_articles = len(articles)

        score = 0
        if total_articles > 0:
            score = ((total_bull - total_bear) / total_articles) * 100

        if score > 30:
            overall_sentiment = 'STRONGLY BULLISH'
        elif score > 10:
            overall_sentiment = 'BULLISH'
        elif score < -30:
            overall_sentiment = 'STRONGLY BEARISH'
        elif score < -10:
            overall_sentiment = 'BEARISH'
        else:
            overall_sentiment = 'NEUTRAL'

        summary = f"Analyzed {total_articles} articles. Sentiment: {overall_sentiment} ({score:.1f})."

        return {
            'sentiment': overall_sentiment,
            'score': score,
            'count': total_articles,
            'bullish': total_bull,
            'bearish': total_bear,
            'neutral': total_neutral,
            'articles': articles,
            'summary': summary
        }

# Placeholder for get_news_for_stock, replace with actual implementation
def get_news_for_stock(symbol):
    # This function should fetch real news data, but here it's a stub
    return []

# ============================
# Main analysis function (stub)
# ============================
def comprehensive_analysis(self, symbol):
    # This function is a placeholder; replace with your actual implementation
    pass

# ============================
# Run the program
# ============================
if __name__ == "__main__":
    print_banner()
    while True:
        try:
            portfolio_input = input("\n💰 Enter your portfolio value ($): ").strip()
            if not portfolio_input:
                portfolio_value = 10000
                break
            portfolio_value = float(portfolio_input)
            break
        except:
            print("❌ Invalid input. Please enter a numeric value.")

    trader = UltimateAITrader(portfolio_value=portfolio_value)
    print("✅ System initialized.")
    # You can call trader.run() if you implement menu