print("\n" + "="*60)
print("🚀 FINALAI PRO STARTING...")
print("="*60 + "\n")
import sys
sys.stdout.flush()
#!/usr/bin/env python3
"""
FinalAI Pro - Advanced AI Trading Analysis Platform
Version: 3.0.0
Author: FinalAI Team
License: MIT

COMPLETE ENHANCED VERSION with:
- Deep Dive Stock Analysis
- Insider Trading Tracking (Buys/Sells)
- Hedge Fund & Institutional Activity
- Pattern Recognition
- News Sentiment Analysis
- SEC Data Integration
- All Security Fixes Applied
- Advanced AI Predictions

Installation:
pip install pandas numpy yfinance python-dotenv rich requests beautifulsoup4 textblob

Optional .env file:
NEWS_API_KEY=your_key_here
SEC_USER_AGENT=YourApp/1.0 (your@email.com)
"""

import os
import sys
import json
import logging
import re
import time
import tempfile
import shutil
import atexit
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import deque

import pandas as pd
import numpy as np
import yfinance as yf
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich import box

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: 'requests' not installed. Some features disabled.")

try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("Warning: 'textblob' not installed. Sentiment analysis disabled.")

# Initialize
console = Console()
load_dotenv()

# Config
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'finalai_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
CONFIG_DIR = Path("data")
CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"
PORTFOLIO_FILE = CONFIG_DIR / "portfolio.json"
CACHE_DIR = CONFIG_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Constants
RSI_OVERSOLD, RSI_OVERBOUGHT = 30, 70
MAX_BATCH_SIZE = 50
RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD = 100, 60.0

# Environment
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "FinalAI/3.0")

# ==========================================
# Data Models
# ==========================================

class TradeType(Enum):
    LONG_TERM = "long_term"
    SWING = "swing"
    DAY_TRADE = "day_trade"
    SCALP = "scalp"

class TrendType(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"

class MarketType(Enum):
    STOCKS = "stocks"
    CRYPTO = "crypto"
    FOREX = "forex"
    FUTURES = "futures"
    INDEXES = "indexes"

@dataclass
class InsiderTransaction:
    name: str
    title: str
    transaction_date: str
    transaction_type: str  # Buy/Sell
    shares: float
    price: float
    value: float

@dataclass
class InstitutionalHolder:
    institution: str
    shares: float
    value: float
    percent_held: float
    change: float
    filing_date: str

@dataclass
class NewsArticle:
    title: str
    source: str
    published_at: str
    url: str
    sentiment_score: float
    sentiment_label: str

@dataclass
class Pattern:
    pattern_type: str
    confidence: float
    description: str
    target_price: Optional[float] = None

@dataclass
class AnalysisResult:
    ticker: str
    signal: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    change_percent: float
    
    # Technical
    rsi: float
    macd: float
    sma_20: float
    sma_50: float
    sma_200: float
    atr: float
    volume_ratio: float
    
    # Advanced
    patterns: List[Pattern] = field(default_factory=list)
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)
    
    # Insider & Institutional
    insider_sentiment: str = "unknown"
    insider_buys: int = 0
    insider_sells: int = 0
    insider_buy_value: float = 0.0
    insider_sell_value: float = 0.0
    recent_insider_transactions: List[InsiderTransaction] = field(default_factory=list)
    
    institutional_ownership: float = 0.0
    institutional_change: float = 0.0
    top_institutions: List[InstitutionalHolder] = field(default_factory=list)
    
    # News
    news_sentiment: float = 0.0
    news_sentiment_label: str = "neutral"
    recent_news: List[NewsArticle] = field(default_factory=list)
    
    # Risk
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    risk_reward: float = 0.0
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

# ==========================================
# Utilities
# ==========================================

class RateLimiter:
    def __init__(self, max_calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
    
    def wait_if_needed(self):
        now = time.time()
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        if len(self.calls) >= self.max_calls:
            sleep_time = self.calls[0] + self.period - now
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.calls.append(now)

class DataFetchError(Exception):
    pass

# ==========================================
# Configuration
# ==========================================

DEFAULT_CONFIG = {
    "ai_name": "FinalAI Pro",
    "version": "3.0.0",
    "confidence_threshold": 75,
    "cache_enabled": True,
    "cache_duration_minutes": 5,
    "max_concurrent_requests": 10,
    
    # AI Settings
    "pattern_detection": True,
    "news_analysis": True,
    "insider_tracking": True,
    "institutional_tracking": True,
    
    # Weights (total 100)
    "weight_technical": 30,
    "weight_patterns": 20,
    "weight_news": 15,
    "weight_insider": 20,
    "weight_institutional": 15,
    
    # Risk
    "default_stop_loss_pct": 5.0,
    "risk_reward_min": 2.0,
    
    "watchlists": {}
}

class ConfigManager:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {**DEFAULT_CONFIG, **config}
            except:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def save(self, config=None):
        try:
            to_save = config or self.config
            with tempfile.NamedTemporaryFile('w', delete=False, 
                                            dir=self.config_file.parent) as f:
                json.dump(to_save, f, indent=2)
                temp_path = f.name
            shutil.move(temp_path, self.config_file)
            self.config = to_save
            return True
        except Exception as e:
            logger.error(f"Save config error: {e}")
            return False
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        return self.save()

# ==========================================
# Cache
# ==========================================

class CacheManager:
    def __init__(self, cache_dir=CACHE_DIR, duration_minutes=5):
        self.cache_dir = cache_dir
        self.duration = timedelta(minutes=duration_minutes)
    
    def _get_key(self, key):
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key):
        cache_file = self.cache_dir / f"{self._get_key(key)}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file) as f:
                data = json.load(f)
            
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.duration:
                cache_file.unlink()
                return None
            
            df = pd.DataFrame(data['data'])
            if df.empty:
                return None
            
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            
            return df
        except:
            return None
    
    def set(self, key, df):
        if df is None or df.empty:
            return False
        
        try:
            cache_file = self.cache_dir / f"{self._get_key(key)}.json"
            df_reset = df.reset_index()
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': df_reset.to_dict(orient='records')
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, default=str)
            return True
        except:
            return False
    
    def clear(self):
        count = 0
        for f in self.cache_dir.glob("*.json"):
            try:
                f.unlink()
                count += 1
            except:
                pass
        return count

# ==========================================
# Data Fetching
# ==========================================

class DataFetcher:
    def __init__(self, config, cache):
        self.config = config
        self.cache = cache
        self.rate_limiter = RateLimiter()
        self.max_workers = config.get('max_concurrent_requests', 10)
    
    def fetch_single(self, ticker, period="1mo", interval="1d", retry=3):
        cache_key = f"{ticker}_{period}_{interval}"
        
        if self.config.get('cache_enabled'):
            cached = self.cache.get(cache_key)
            if cached is not None:
                return ticker, cached
        
        self.rate_limiter.wait_if_needed()
        
        for attempt in range(retry):
            try:
                df = yf.download(ticker, period=period, interval=interval, 
                               progress=False, auto_adjust=True)
                
                if not df.empty:
                    if self.config.get('cache_enabled'):
                        self.cache.set(cache_key, df)
                    return ticker, df
                
                time.sleep(2 ** attempt)
            except Exception as e:
                if attempt == retry - 1:
                    logger.error(f"Failed to fetch {ticker}: {e}")
                time.sleep(2 ** attempt)
        
        return ticker, pd.DataFrame()
    
    def fetch_batch(self, tickers, period="1mo", interval="1d"):
        results = {}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                     BarColumn(), console=console, transient=True) as progress:
            task = progress.add_task(f"[cyan]Fetching {len(tickers)} ticker(s)...", 
                                    total=len(tickers))
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self.fetch_single, t, period, interval): t 
                          for t in tickers}
                
                for future in as_completed(futures):
                    ticker, df = future.result()
                    results[ticker] = df
                    progress.advance(task)
        
        return results

# ==========================================
# Technical Analysis
# ==========================================

class TechnicalAnalyzer:
    @staticmethod
    def calculate_rsi(series, period=14):
        if len(series) < period + 1:
            return 50.0
        
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = -delta.clip(upper=0).rolling(period).mean()
        
        if loss.iloc[-1] == 0:
            return 100.0 if gain.iloc[-1] > 0 else 50.0
        
        rs = gain.iloc[-1] / loss.iloc[-1]
        return 100.0 - (100.0 / (1.0 + rs))
    
    @staticmethod
    def calculate_macd(series):
        if len(series) < 26:
            return 0.0, 0.0
        
        exp1 = series.ewm(span=12, adjust=False).mean()
        exp2 = series.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return float(macd.iloc[-1]), float(signal.iloc[-1])
    
    @staticmethod
    def calculate_atr(df, period=14):
        if len(df) < period or 'High' not in df.columns:
            return 0.0
        
        try:
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            
            return float(atr.iloc[-1])
        except:
            return 0.0
    
    @staticmethod
    def detect_patterns(df):
        patterns = []
        
        if len(df) < 60:
            return patterns
        
        try:
            close = df['Close'].values
            
            # Head & Shoulders (simplified)
            window = 10
            peaks = []
            for i in range(window, len(df) - window):
                if df['High'].iloc[i] == df['High'].iloc[i-window:i+window].max():
                    peaks.append((i, df['High'].iloc[i]))
            
            if len(peaks) >= 3:
                recent = peaks[-3:]
                if recent[1][1] > recent[0][1] and recent[1][1] > recent[2][1]:
                    patterns.append(Pattern(
                        pattern_type="Head & Shoulders",
                        confidence=75.0,
                        description="Bearish reversal pattern detected"
                    ))
            
            # Double Top/Bottom
            if len(peaks) >= 2:
                last_two = peaks[-2:]
                if abs(last_two[0][1] - last_two[1][1]) / last_two[0][1] < 0.03:
                    patterns.append(Pattern(
                        pattern_type="Double Top",
                        confidence=70.0,
                        description="Bearish pattern - potential reversal"
                    ))
        except:
            pass
        
        return patterns
    
    @staticmethod
    def find_support_resistance(df, window=20):
        supports = []
        resistances = []
        
        if len(df) < window * 2:
            return supports, resistances
        
        try:
            for i in range(window, len(df) - window):
                # Support
                if df['Low'].iloc[i] == df['Low'].iloc[i-window:i+window].min():
                    supports.append(float(df['Low'].iloc[i]))
                
                # Resistance
                if df['High'].iloc[i] == df['High'].iloc[i-window:i+window].max():
                    resistances.append(float(df['High'].iloc[i]))
            
            supports = sorted(set(supports), reverse=True)[:3]
            resistances = sorted(set(resistances))[:3]
        except:
            pass
        
        return supports, resistances

# ==========================================
# News & Sentiment
# ==========================================

class NewsAnalyzer:
    def __init__(self):
        pass
    
    def fetch_news(self, ticker, days=7):
        articles = []
        
        try:
            stock = yf.Ticker(ticker)
            if hasattr(stock, 'news'):
                for item in stock.news[:10]:
                    sentiment_score, sentiment_label = self._analyze_sentiment(
                        item.get('title', '') + ' ' + item.get('summary', '')
                    )
                    
                    articles.append(NewsArticle(
                        title=item.get('title', 'No title'),
                        source=item.get('publisher', 'Unknown'),
                        published_at=datetime.fromtimestamp(
                            item.get('providerPublishTime', time.time())
                        ).isoformat(),
                        url=item.get('link', ''),
                        sentiment_score=sentiment_score,
                        sentiment_label=sentiment_label
                    ))
        except Exception as e:
            logger.error(f"News fetch error for {ticker}: {e}")
        
        return articles
    
    def _analyze_sentiment(self, text):
        if not SENTIMENT_AVAILABLE or not text:
            return 0.0, "neutral"
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return polarity, "positive"
            elif polarity < -0.1:
                return polarity, "negative"
            else:
                return polarity, "neutral"
        except:
            return 0.0, "neutral"
    
    def get_overall_sentiment(self, articles):
        if not articles:
            return 0.0, "neutral"
        
        avg = np.mean([a.sentiment_score for a in articles])
        
        if avg > 0.2:
            return float(avg), "positive"
        elif avg < -0.2:
            return float(avg), "negative"
        else:
            return float(avg), "neutral"

# ==========================================
# SEC / Insider Data
# ==========================================

class SECDataFetcher:
    def __init__(self):
        self.user_agent = SEC_USER_AGENT
    
    def fetch_insider_transactions(self, ticker, days=90):
        transactions = []
        
        try:
            stock = yf.Ticker(ticker)
            
            if hasattr(stock, 'insider_transactions'):
                insider_data = stock.insider_transactions
                
                if insider_data is not None and not insider_data.empty:
                    cutoff_date = datetime.now() - timedelta(days=days)
                    
                    for _, row in insider_data.head(50).iterrows():
                        try:
                            trans_date = pd.to_datetime(row.get('Start Date', 
                                                               row.get('Date', datetime.now())))
                            
                            if trans_date < cutoff_date:
                                continue
                            
                            trans_type = str(row.get('Transaction', ''))
                            if 'purchase' in trans_type.lower() or 'buy' in trans_type.lower():
                                trans_type = 'Buy'
                            elif 'sale' in trans_type.lower() or 'sell' in trans_type.lower():
                                trans_type = 'Sell'
                            else:
                                trans_type = 'Other'
                            
                            transactions.append(InsiderTransaction(
                                name=str(row.get('Insider Trading', row.get('Insider', 'Unknown'))),
                                title=str(row.get('Position', 'Unknown')),
                                transaction_date=str(trans_date.date()),
                                transaction_type=trans_type,
                                shares=float(row.get('Shares', 0)),
                                price=float(row.get('Price', 0)),
                                value=float(row.get('Value', 0))
                            ))
                        except:
                            continue
        except Exception as e:
            logger.error(f"Insider fetch error for {ticker}: {e}")
        
        return transactions
    
    def fetch_institutional_holders(self, ticker):
        holders = []
        
        try:
            stock = yf.Ticker(ticker)
            
            if hasattr(stock, 'institutional_holders'):
                inst_data = stock.institutional_holders
                
                if inst_data is not None and not inst_data.empty:
                    for _, row in inst_data.head(10).iterrows():
                        try:
                            holders.append(InstitutionalHolder(
                                institution=str(row.get('Holder', 'Unknown')),
                                shares=float(row.get('Shares', 0)),
                                value=float(row.get('Value', 0)),
                                percent_held=float(row.get('% Out', 0)),
                                change=0.0,  # Would need historical data
                                filing_date=str(row.get('Date Reported', ''))
                            ))
                        except:
                            continue
        except Exception as e:
            logger.error(f"Institutional fetch error for {ticker}: {e}")
        
        return holders
    
    def analyze_insider_sentiment(self, transactions):
        if not transactions:
            return {
                'sentiment': 'unknown',
                'buys': 0,
                'sells': 0,
                'buy_value': 0.0,
                'sell_value': 0.0
            }
        
        buys = [t for t in transactions if t.transaction_type == 'Buy']
        sells = [t for t in transactions if t.transaction_type == 'Sell']
        
        buy_value = sum(t.value for t in buys)
        sell_value = sum(t.value for t in sells)
        
        net = buy_value - sell_value
        
        if net > sell_value * 0.5:
            sentiment = 'bullish'
        elif net < -buy_value * 0.5:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'buys': len(buys),
            'sells': len(sells),
            'buy_value': buy_value,
            'sell_value': sell_value
        }

# ==========================================
# Comprehensive Analyzer
# ==========================================

class ComprehensiveAnalyzer:
    def __init__(self, config, fetcher):
        self.config = config
        self.fetcher = fetcher
        self.technical = TechnicalAnalyzer()
        self.news_analyzer = NewsAnalyzer()
        self.sec_fetcher = SECDataFetcher()
    
    def analyze(self, ticker, df):
        if df.empty or len(df) < 50:
            return self._empty_result(ticker)
        
        try:
            close = df['Close']
            price = float(close.iloc[-1])
            prev_price = float(close.iloc[-2]) if len(close) > 1 else price
            change_pct = ((price - prev_price) / prev_price) * 100
            
            # Technical indicators
            rsi = self.technical.calculate_rsi(close)
            macd, macd_signal = self.technical.calculate_macd(close)
            atr = self.technical.calculate_atr(df)
            
            sma_20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else price
            sma_50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else price
            sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(df) >= 200 else price
            
            volume = int(df['Volume'].iloc[-1]) if 'Volume' in df.columns else 0
            avg_volume = int(df['Volume'].tail(20).mean()) if 'Volume' in df.columns else 1
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            
            # Patterns
            patterns = []
            if self.config.get('pattern_detection'):
                patterns = self.technical.detect_patterns(df)
            
            # Support/Resistance
            supports, resistances = self.technical.find_support_resistance(df)
            
            # Insider data
            insider_data = {'sentiment': 'unknown', 'buys': 0, 'sells': 0, 
                          'buy_value': 0.0, 'sell_value': 0.0}
            insider_transactions = []
            
            if self.config.get('insider_tracking'):
                insider_transactions = self.sec_fetcher.fetch_insider_transactions(ticker)
                insider_data = self.sec_fetcher.analyze_insider_sentiment(insider_transactions)
            
            # Institutional data
            institutional_holders = []
            inst_ownership = 0.0
            inst_change = 0.0
            
            if self.config.get('institutional_tracking'):
                institutional_holders = self.sec_fetcher.fetch_institutional_holders(ticker)
                if institutional_holders:
                    inst_ownership = sum(h.percent_held for h in institutional_holders)
            
            # News sentiment
            news_articles = []
            news_score = 0.0
            news_label = "neutral"
            
            if self.config.get('news_analysis'):
                news_articles = self.news_analyzer.fetch_news(ticker)
                news_score, news_label = self.news_analyzer.get_overall_sentiment(news_articles)
            
            # Generate signal
            signal_data = self._generate_signal(
                price, rsi, macd, macd_signal, sma_20, sma_50, sma_200,
                patterns, insider_data, inst_ownership, news_score, volume_ratio
            )
            
            # Risk management
            stop_loss = price * (1 - self.config.get('default_stop_loss_pct', 5) / 100)
            if supports:
                stop_loss = max(stop_loss, supports[0] * 0.99)
            
            target = price * 1.1
            if resistances:
                target = resistances[0] * 0.99
            
            risk = price - stop_loss
            reward = target - price
            risk_reward = reward / risk if risk > 0 else 0.0
            
            return AnalysisResult(
                ticker=ticker,
                signal=signal_data['signal'],
                confidence=signal_data['confidence'],
                price=round(price, 2),
                change_percent=round(change_pct, 2),
                rsi=round(rsi, 2),
                macd=round(macd, 4),
                sma_20=round(sma_20, 2),
                sma_50=round(sma_50, 2),
                sma_200=round(sma_200, 2),
                atr=round(atr, 2),
                volume_ratio=round(volume_ratio, 2),
                patterns=patterns,
                support_levels=supports,
                resistance_levels=resistances,
                insider_sentiment=insider_data['sentiment'],
                insider_buys=insider_data['buys'],
                insider_sells=insider_data['sells'],
                insider_buy_value=round(insider_data['buy_value'], 2),
                insider_sell_value=round(insider_data['sell_value'], 2),
                recent_insider_transactions=insider_transactions[:10],
                institutional_ownership=round(inst_ownership, 2),
                institutional_change=round(inst_change, 2),
                top_institutions=institutional_holders[:5],
                news_sentiment=round(news_score, 3),
                news_sentiment_label=news_label,
                recent_news=news_articles[:5],
                stop_loss=round(stop_loss, 2),
                target=round(target, 2),
                risk_reward=round(risk_reward, 2)
            )
        
        except Exception as e:
            logger.error(f"Analysis error for {ticker}: {e}")
            return self._empty_result(ticker)
    
    def _generate_signal(self, price, rsi, macd, macd_signal, sma_20, sma_50, sma_200,
                        patterns, insider_data, inst_ownership, news_score, volume_ratio):
        
        weights = {
            'technical': self.config.get('weight_technical', 30),
            'patterns': self.config.get('weight_patterns', 20),
            'news': self.config.get('weight_news', 15),
            'insider': self.config.get('weight_insider', 20),
            'institutional': self.config.get('weight_institutional', 15)
        }
        
        scores = []
        
        # Technical score
        tech_score = 0
        if price > sma_20 > sma_50:
            tech_score += 30
        elif price < sma_20 < sma_50:
            tech_score -= 30
        
        if rsi < RSI_OVERSOLD:
            tech_score += 25
        elif rsi > RSI_OVERBOUGHT:
            tech_score -= 25
        
        if macd > macd_signal:
            tech_score += 25
        elif macd < macd_signal:
            tech_score -= 25
        
        scores.append(('technical', tech_score, weights['technical']))
        
        # Pattern score
        pattern_score = 0
        for p in patterns:
            if 'bearish' in p.description.lower():
                pattern_score -= p.confidence / 2
            elif 'bullish' in p.description.lower():
                pattern_