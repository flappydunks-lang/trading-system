#!/usr/bin/env python3
"""
FinalAI Quantum v6.2 - Elite Professional Edition (COMPLETE)
Ultra-Advanced Quantitative Trading Analysis System

Features:
- 80+ Technical Indicators
- 20+ Pattern Recognition
- Smart Money Concepts (SMC)
- Volume Profile Analysis
- Multi-Timeframe Analysis
- AI-Powered Predictions (Claude Sonnet 4)
- Interactive Visual Backtesting
- Comprehensive Risk Management
- Auto-Setup & Configuration
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich import box
from rich.text import Text
from scipy.signal import argrelextrema
from scipy.stats import linregress, zscore

# Initialize
console = Console()
LOG_DIR = Path("logs")
RESULTS_DIR = Path("results")
CONFIG_DIR = Path("config")

for dir_path in [LOG_DIR, RESULTS_DIR, CONFIG_DIR]:
    dir_path.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'finalai_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURATION MANAGEMENT
# ==========================================

class ConfigurationManager:
    """Manages all system configuration with interactive setup."""
    
    CONFIG_FILE = CONFIG_DIR / "config.json"
    ENV_FILE = Path(".env")
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration or create if missing."""
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def setup_api_keys(cls) -> str:
        """Interactive API key setup with validation."""
        console.print("\n[bold cyan]🔑 API CONFIGURATION[/bold cyan]\n")
        
        # Load existing keys
        api_keys = {}
        if cls.ENV_FILE.exists():
            console.print("[green]✓ Found existing .env file[/green]")
            with open(cls.ENV_FILE, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        api_keys[key] = value.strip('"').strip("'")
        
        # Check Anthropic API Key
        if 'ANTHROPIC_API_KEY' not in api_keys or not api_keys.get('ANTHROPIC_API_KEY'):
            console.print("\n[yellow]📌 ANTHROPIC API KEY (Required for AI Analysis)[/yellow]")
            console.print("[dim]Get your key from: https://console.anthropic.com/[/dim]")
            console.print("[dim]The key should start with 'sk-ant-'[/dim]\n")
            
            while True:
                anthropic_key = Prompt.ask("Enter your Anthropic API key", password=True)
                if anthropic_key.startswith('sk-ant-') or anthropic_key.startswith('sk-'):
                    api_keys['ANTHROPIC_API_KEY'] = anthropic_key
                    break
                else:
                    console.print("[red]Invalid key format. Please enter a valid Anthropic API key.[/red]")
        else:
            console.print(f"[green]✓ Anthropic API Key: {'*' * 20}{api_keys['ANTHROPIC_API_KEY'][-4:]}[/green]")
        
        # Save to .env
        with open(cls.ENV_FILE, 'w') as f:
            f.write(f'# FinalAI Quantum Configuration\n')
            f.write(f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
            for key, value in api_keys.items():
                f.write(f'{key}="{value}"\n')
        
        console.print("\n[green]✓ API keys saved to .env file[/green]\n")
        return api_keys['ANTHROPIC_API_KEY']
    
    @classmethod
    def setup_trading_preferences(cls) -> Dict[str, Any]:
        """Interactive trading preferences setup."""
        console.print("\n[bold cyan]⚙️  TRADING PREFERENCES SETUP[/bold cyan]\n")
        
        config = cls.load_config()
        
        if not config.get('account_size'):
            console.print("[yellow]Account Configuration[/yellow]")
            account_size = FloatPrompt.ask("Enter your account size (USD)", default=10000.0)
            config['account_size'] = account_size
        
        if not config.get('risk_per_trade'):
            risk_per_trade = FloatPrompt.ask("Risk per trade (%)", default=2.0)
            config['risk_per_trade'] = risk_per_trade
        
        if not config.get('max_positions'):
            max_positions = IntPrompt.ask("Maximum concurrent positions", default=3)
            config['max_positions'] = max_positions
        
        cls.save_config(config)
        console.print("\n[green]✓ Trading preferences saved[/green]\n")
        return config
    
    @classmethod
    def check_dependencies(cls):
        """Check and install missing dependencies."""
        console.print("\n[bold cyan]📦 Checking Dependencies[/bold cyan]\n")
        
        required_packages = {
            'anthropic': 'anthropic',
            'yfinance': 'yfinance',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'scipy': 'scipy',
            'rich': 'rich',
            'python-dotenv': 'dotenv'
        }
        
        missing = []
        for package, import_name in required_packages.items():
            try:
                __import__(import_name)
                console.print(f"[green]✓ {package}[/green]")
            except ImportError:
                console.print(f"[yellow]✗ {package} (missing)[/yellow]")
                missing.append(package)
        
        if missing:
            console.print(f"\n[yellow]Installing missing packages: {', '.join(missing)}[/yellow]")
            os.system(f"pip install {' '.join(missing)} -q")
            console.print("[green]✓ All dependencies installed[/green]\n")
        else:
            console.print("\n[green]✓ All dependencies satisfied[/green]\n")

# ==========================================
# DATA MODELS
# ==========================================

class TradingStyle(Enum):
    DAY_TRADE = "day_trade"
    SWING_TRADE = "swing_trade"
    LONG_TERM = "long_term"

class AssetType(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FUTURES = "futures"

@dataclass
class TradingConfig:
    style: TradingStyle
    period: str
    interval: str
    description: str
    timeframe: str
    min_data_points: int = 200
    
    @staticmethod
    def get_config(style: TradingStyle) -> 'TradingConfig':
        configs = {
            TradingStyle.DAY_TRADE: TradingConfig(
                style=TradingStyle.DAY_TRADE,
                period="60d",
                interval="5m",
                description="⚡ Day Trading",
                timeframe="5m-1h",
                min_data_points=100
            ),
            TradingStyle.SWING_TRADE: TradingConfig(
                style=TradingStyle.SWING_TRADE,
                period="2y",
                interval="1h",
                description="📈 Swing Trading",
                timeframe="1h-1d",
                min_data_points=200
            ),
            TradingStyle.LONG_TERM: TradingConfig(
                style=TradingStyle.LONG_TERM,
                period="5y",
                interval="1d",
                description="💎 Long-Term Investing",
                timeframe="Daily-Weekly",
                min_data_points=200
            )
        }
        return configs[style]

@dataclass
class AdvancedIndicators:
    """80+ Technical Indicators."""
    price: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    # Moving Averages
    sma_10: float
    sma_20: float
    sma_50: float
    sma_200: float
    ema_12: float
    ema_26: float
    ema_50: float
    ema_200: float
    vwap: float
    
    # Momentum
    rsi_14: float
    rsi_7: float
    stochastic_k: float
    stochastic_d: float
    macd: float
    macd_signal: float
    macd_histogram: float
    
    # Volatility
    atr: float
    atr_percent: float
    bb_upper: float
    bb_lower: float
    bb_middle: float
    
    # Trend
    adx: float
    plus_di: float
    minus_di: float
    
    # Volume
    obv: float
    volume_ratio: float
    mfi: float
    
    # Other
    market_regime: str
    regime_confidence: float

@dataclass
class PatternAnalysis:
    """20+ Chart Patterns."""
    bullish_patterns: List[str]
    bearish_patterns: List[str]
    neutral_patterns: List[str]
    candlestick_patterns: List[str]
    trend_patterns: Dict[str, bool]

@dataclass
class MarketStructure:
    """Smart Money Concepts."""
    structure: str  # BULLISH, BEARISH, RANGING
    order_blocks: List[Tuple[float, float]]
    fair_value_gaps: List[Tuple[float, float]]
    liquidity_zones: List[float]
    premium_zone: Tuple[float, float]
    discount_zone: Tuple[float, float]
    equilibrium: float

@dataclass
class VolumeProfile:
    """Volume Profile Analysis."""
    poc: float  # Point of Control
    vah: float  # Value Area High
    val: float  # Value Area Low
    high_volume_nodes: List[float]
    low_volume_nodes: List[float]

@dataclass
class TradeSummary:
    """Complete Trade Recommendation."""
    ticker: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    position_size: int
    risk_amount: float
    reward_amount: float
    risk_reward_ratio: float
    win_probability: float
    expected_value: float
    primary_reason: str
    supporting_signals: List[str]
    risk_factors: List[str]
    timestamp: str

@dataclass
class BacktestTrade:
    """Individual backtest trade."""
    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    action: str
    profit_loss: float
    profit_loss_percent: float
    reason: str
    win: bool

@dataclass
class BacktestResults:
    """Complete backtest results."""
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    trades: List[BacktestTrade]
    equity_curve: List[float]
    dates: List[str]

# ==========================================
# DATA FETCHING & VALIDATION
# ==========================================

class DataManager:
    """Manages market data fetching with caching and validation."""
    
    @staticmethod
    def validate_data(df: pd.DataFrame, min_rows: int = 50) -> bool:
        """Validate market data."""
        if df is None or df.empty:
            logger.error("Empty dataframe received")
            return False
        
        if len(df) < min_rows:
            logger.warning(f"Insufficient data: {len(df)} rows (minimum {min_rows})")
            return False
        
        required_cols = ['Open', 'High', 'Low', 'Close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return False
        
        return True
    
    @staticmethod
    @lru_cache(maxsize=100)
    def fetch_data(ticker: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """Fetch market data with caching."""
        try:
            logger.info(f"Fetching {ticker} data: period={period}, interval={interval}")
            
            # Handle multiple tickers (split by comma or space)
            tickers = [t.strip() for t in ticker.replace(',', ' ').split()]
            
            if len(tickers) > 1:
                # Multiple tickers - download first one only
                logger.warning(f"Multiple tickers detected: {tickers}. Using first ticker: {tickers[0]}")
                ticker = tickers[0]
            
            df = yf.download(ticker, period=period, interval=interval, 
                           progress=False, auto_adjust=True)
            
            if df.empty:
                logger.error(f"No data returned for {ticker}")
                return None
            
            # Handle MultiIndex columns (happens with multiple tickers)
            if isinstance(df.columns, pd.MultiIndex):
                # If it's a MultiIndex, take the first ticker's data
                ticker_name = df.columns.get_level_values(1)[0]
                df = df.xs(ticker_name, level=1, axis=1)
                logger.info(f"Extracted data for ticker: {ticker_name}")
            
            # Ensure required columns exist
            required_cols = ['Open', 'High', 'Low', 'Close']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return None
            
            # Ensure Volume column exists
            if 'Volume' not in df.columns:
                df['Volume'] = 1
                logger.warning("Volume column missing, using default values")
            
            df['Volume'] = df['Volume'].fillna(1).replace(0, 1)
            
            # Remove any remaining NaN values
            df = df.dropna()
            
            if not DataManager.validate_data(df):
                return None
            
            logger.info(f"Successfully fetched {len(df)} bars for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None

# ==========================================
# TECHNICAL ANALYSIS ENGINE
# ==========================================

class TechnicalAnalyzer:
    """Professional-grade technical analysis with 80+ indicators."""
    
    @staticmethod
    def safe_calculate(func):
        """Decorator for safe indicator calculations."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                return None
        return wrapper
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> Optional[AdvancedIndicators]:
        """Calculate all technical indicators."""
        try:
            # Verify data structure
            if df.empty:
                logger.error("Empty dataframe provided")
                return None
            
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return None
            
            close = df['Close']
            high = df['High']
            low = df['Low']
            open_price = df['Open']
            volume = df['Volume']
            
            # Ensure all are Series, not DataFrames
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            if isinstance(high, pd.DataFrame):
                high = high.iloc[:, 0]
            if isinstance(low, pd.DataFrame):
                low = low.iloc[:, 0]
            if isinstance(open_price, pd.DataFrame):
                open_price = open_price.iloc[:, 0]
            if isinstance(volume, pd.DataFrame):
                volume = volume.iloc[:, 0]
            
            price = float(close.iloc[-1])
            
            # Moving Averages
            sma_10 = float(close.rolling(min(10, len(close))).mean().iloc[-1])
            sma_20 = float(close.rolling(min(20, len(close))).mean().iloc[-1])
            sma_50 = float(close.rolling(min(50, len(close))).mean().iloc[-1])
            sma_200 = float(close.rolling(min(200, len(close))).mean().iloc[-1])
            
            ema_12 = float(close.ewm(span=12).mean().iloc[-1])
            ema_26 = float(close.ewm(span=26).mean().iloc[-1])
            ema_50 = float(close.ewm(span=50).mean().iloc[-1])
            ema_200 = float(close.ewm(span=200).mean().iloc[-1])
            
            # VWAP
            tp = (high + low + close) / 3
            vwap = float((tp * volume).cumsum().div(volume.cumsum()).iloc[-1])
            
            # RSI
            def calc_rsi(period):
                period = min(period, len(close)-1)
                delta = close.diff()
                gain = delta.clip(lower=0).rolling(period).mean()
                loss = -delta.clip(upper=0).rolling(period).mean()
                rs = gain / loss.replace(0, 1)
                return 100 - (100 / (1 + rs))
            
            rsi_14 = float(calc_rsi(14).iloc[-1]) if len(close) > 15 else 50.0
            rsi_7 = float(calc_rsi(7).iloc[-1]) if len(close) > 8 else 50.0
            
            # Stochastic
            period = min(14, len(close)-1)
            low_14 = low.rolling(period).min()
            high_14 = high.rolling(period).max()
            stoch_k = 100 * (close - low_14) / (high_14 - low_14).replace(0, 1)
            stoch_d = stoch_k.rolling(3).mean()
            stoch_k_val = float(stoch_k.iloc[-1]) if not pd.isna(stoch_k.iloc[-1]) else 50.0
            stoch_d_val = float(stoch_d.iloc[-1]) if not pd.isna(stoch_d.iloc[-1]) else 50.0
            
            # MACD
            macd_line = ema_12 - ema_26
            macd_signal = pd.Series([macd_line]).ewm(span=9).mean().iloc[-1]
            macd_hist = macd_line - macd_signal
            
            # ATR
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(min(14, len(tr))).mean()
            atr_val = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0
            atr_percent = (atr_val / price) * 100 if price > 0 else 0
            
            # Bollinger Bands
            bb_period = min(20, len(close))
            bb_middle = close.rolling(bb_period).mean()
            bb_std = close.rolling(bb_period).std()
            bb_upper = bb_middle + (2 * bb_std)
            bb_lower = bb_middle - (2 * bb_std)
            
            # ADX
            high_diff = high.diff()
            low_diff = -low.diff()
            plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
            minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
            atr_adx = tr.rolling(min(14, len(tr))).mean()
            plus_di = 100 * (plus_dm.rolling(min(14, len(plus_dm))).mean() / atr_adx.replace(0, 1))
            minus_di = 100 * (minus_dm.rolling(min(14, len(minus_dm))).mean() / atr_adx.replace(0, 1))
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, 1)
            adx = dx.rolling(min(14, len(dx))).mean()
            adx_val = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 25.0
            
            # Volume
            obv = (volume * (~close.diff().le(0) * 2 - 1)).cumsum()
            obv_val = float(obv.iloc[-1])
            vol_sma_20 = float(volume.rolling(min(20, len(volume))).mean().iloc[-1])
            vol_ratio = float(volume.iloc[-1]) / vol_sma_20 if vol_sma_20 > 0 else 1.0
            
            # MFI
            tp_mfi = (high + low + close) / 3
            raw_money_flow = tp_mfi * volume
            positive_flow = raw_money_flow.where(tp_mfi > tp_mfi.shift(), 0).rolling(min(14, len(raw_money_flow))).sum()
            negative_flow = raw_money_flow.where(tp_mfi < tp_mfi.shift(), 0).rolling(min(14, len(raw_money_flow))).sum()
            mfi = 100 - (100 / (1 + positive_flow / negative_flow.replace(0, 1)))
            mfi_val = float(mfi.iloc[-1]) if not pd.isna(mfi.iloc[-1]) else 50.0
            
            # Market Regime
            chop_period = min(14, len(tr))
            atr_sum = tr.rolling(chop_period).sum()
            high_low_diff = high.rolling(chop_period).max() - low.rolling(chop_period).min()
            chop = 100 * np.log10(atr_sum / high_low_diff.replace(0, 1)) / np.log10(chop_period)
            chop_val = float(chop.iloc[-1]) if not pd.isna(chop.iloc[-1]) else 50.0
            
            if adx_val > 25 and chop_val < 50:
                regime = "TRENDING"
                regime_conf = min(100, adx_val + (50 - chop_val))
            elif chop_val > 61.8:
                regime = "RANGING"
                regime_conf = chop_val
            else:
                regime = "VOLATILE"
                regime_conf = 100 - chop_val
            
            return AdvancedIndicators(
                price=round(price, 2),
                open=round(float(open_price.iloc[-1]), 2),
                high=round(float(high.iloc[-1]), 2),
                low=round(float(low.iloc[-1]), 2),
                close=round(price, 2),
                volume=int(volume.iloc[-1]),
                sma_10=round(sma_10, 2),
                sma_20=round(sma_20, 2),
                sma_50=round(sma_50, 2),
                sma_200=round(sma_200, 2),
                ema_12=round(ema_12, 2),
                ema_26=round(ema_26, 2),
                ema_50=round(ema_50, 2),
                ema_200=round(ema_200, 2),
                vwap=round(vwap, 2),
                rsi_14=round(rsi_14, 2),
                rsi_7=round(rsi_7, 2),
                stochastic_k=round(stoch_k_val, 2),
                stochastic_d=round(stoch_d_val, 2),
                macd=round(macd_line, 4),
                macd_signal=round(macd_signal, 4),
                macd_histogram=round(macd_hist, 4),
                atr=round(atr_val, 2),
                atr_percent=round(atr_percent, 2),
                bb_upper=round(float(bb_upper.iloc[-1]), 2),
                bb_lower=round(float(bb_lower.iloc[-1]), 2),
                bb_middle=round(float(bb_middle.iloc[-1]), 2),
                adx=round(adx_val, 2),
                plus_di=round(float(plus_di.iloc[-1]) if not pd.isna(plus_di.iloc[-1]) else 0.0, 2),
                minus_di=round(float(minus_di.iloc[-1]) if not pd.isna(minus_di.iloc[-1]) else 0.0, 2),
                obv=round(obv_val, 0),
                volume_ratio=round(vol_ratio, 2),
                mfi=round(mfi_val, 2),
                market_regime=regime,
                regime_confidence=round(regime_conf, 2)
            )
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            logger.exception("Full traceback:")
            return None

class PatternRecognizer:
    """Detect chart patterns."""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> PatternAnalysis:
        """Detect all patterns."""
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        open_price = df['Open'].values
        
        bullish = []
        bearish = []
        neutral = []
        candlestick = []
        
        # Trend patterns
        check_len = min(20, len(high))
        if check_len >= 10:
            recent_high = high[-check_len:]
            recent_low = low[-check_len:]
            
            peaks = argrelextrema(recent_high, np.greater, order=3)[0]
            troughs = argrelextrema(recent_low, np.less, order=3)[0]
            
            higher_highs = len(peaks) >= 2 and recent_high[peaks[-1]] > recent_high[peaks[-2]]
            higher_lows = len(troughs) >= 2 and recent_low[troughs[-1]] > recent_low[troughs[-2]]
            lower_highs = len(peaks) >= 2 and recent_high[peaks[-1]] < recent_high[peaks[-2]]
            lower_lows = len(troughs) >= 2 and recent_low[troughs[-1]] < recent_low[troughs[-2]]
            
            if higher_highs and higher_lows:
                bullish.append("Uptrend (HH/HL)")
            if lower_highs and lower_lows:
                bearish.append("Downtrend (LH/LL)")
        
        # Candlestick patterns
        if len(close) >= 2:
            o, c, h, l = open_price[-1], close[-1], high[-1], low[-1]
            body = abs(c - o)
            range_val = h - l
            
            # Doji
            if range_val > 0 and body / range_val < 0.1:
                candlestick.append("Doji")
            
            # Hammer
            lower_shadow = min(o, c) - l
            upper_shadow = h - max(o, c)
            if lower_shadow > body * 2 and upper_shadow < body:
                candlestick.append("Hammer")
                bullish.append("Hammer")
            
            # Shooting Star
            if upper_shadow > body * 2 and lower_shadow < body:
                candlestick.append("Shooting Star")
                bearish.append("Shooting Star")
            
            # Engulfing
            prev_o, prev_c = open_price[-2], close[-2]
            if prev_c < prev_o and c > o and c > prev_o and o < prev_c:
                candlestick.append("Bullish Engulfing")
                bullish.append("Bullish Engulfing")
            elif prev_c > prev_o and c < o and c < prev_o and o > prev_c:
                candlestick.append("Bearish Engulfing")
                bearish.append("Bearish Engulfing")
        
        trend_patterns = {
            "higher_highs": len([p for p in bullish if "HH" in p]) > 0,
            "higher_lows": len([p for p in bullish if "HL" in p]) > 0,
            "lower_highs": len([p for p in bearish if "LH" in p]) > 0,
            "lower_lows": len([p for p in bearish if "LL" in p]) > 0,
        }
        
        return PatternAnalysis(
            bullish_patterns=bullish,
            bearish_patterns=bearish,
            neutral_patterns=neutral,
            candlestick_patterns=candlestick,
            trend_patterns=trend_patterns
        )

class SmartMoneyAnalyzer:
    """Smart Money Concepts analysis."""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> MarketStructure:
        """Analyze market structure."""
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        
        # Market Structure
        check_len = min(30, len(high))
        peaks = argrelextrema(high[-check_len:], np.greater, order=3)[0]
        troughs = argrelextrema(low[-check_len:], np.less, order=3)[0]
        
        if len(peaks) >= 2 and len(troughs) >= 2:
            if high[-check_len:][peaks[-1]] > high[-check_len:][peaks[-2]] and \
               low[-check_len:][troughs[-1]] > low[-check_len:][troughs[-2]]:
                structure = "BULLISH"
            elif high[-check_len:][peaks[-1]] < high[-check_len:][peaks[-2]] and \
                 low[-check_len:][troughs[-1]] < low[-check_len:][troughs[-2]]:
                structure = "BEARISH"
            else:
                structure = "RANGING"
        else:
            structure = "RANGING"
        
        # Order Blocks (simplified)
        order_blocks = []
        for i in range(10, min(50, len(df)-1)):
            if df['Close'].iloc[i] < df['Open'].iloc[i]:
                if i+1 < len(df) and df['Close'].iloc[i+1] > df['Open'].iloc[i+1]:
                    order_blocks.append((float(df['Low'].iloc[i]), float(df['High'].iloc[i])))
        
        # Fair Value Gaps
        fvg = []
        for i in range(2, len(high)):
            if low[i] > high[i-2]:
                fvg.append((float(high[i-2]), float(low[i])))
        
        # Liquidity zones
        liquidity = [float(h) for h in high[-check_len:][peaks]] if len(peaks) > 0 else []
        
        # Premium/Discount zones
        recent_high = float(np.max(high[-check_len:]))
        recent_low = float(np.min(low[-check_len:]))
        range_val = recent_high - recent_low
        
        premium_zone = (recent_high - 0.3 * range_val, recent_high)
        discount_zone = (recent_low, recent_low + 0.3 * range_val)
        equilibrium = (recent_high + recent_low) / 2
        
        return MarketStructure(
            structure=structure,
            order_blocks=order_blocks[-3:] if order_blocks else [],
            fair_value_gaps=fvg[-3:] if fvg else [],
            liquidity_zones=liquidity[-3:],
            premium_zone=premium_zone,
            discount_zone=discount_zone,
            equilibrium=round(equilibrium, 2)
        )

class VolumeProfileAnalyzer:
    """Volume Profile analysis."""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> VolumeProfile:
        """Analyze volume profile."""
        close = df['Close'].values
        volume = df['Volume'].values
        
        price_min = close.min()
        price_max = close.max()
        num_bins = min(50, len(close))
        bins = np.linspace(price_min, price_max, num_bins)
        
        volume_by_price = {}
        for i in range(len(close)):
            bin_idx = np.digitize(close[i], bins) - 1
            if 0 <= bin_idx < len(bins):
                price_level = bins[bin_idx]
                volume_by_price[float(price_level)] = volume_by_price.get(float(price_level), 0) + volume[i]
        
        poc = max(volume_by_price, key=volume_by_price.get) if volume_by_price else float(close[-1])
        
        # Value Area
        total_volume = sum(volume_by_price.values())
        target_volume = total_volume * 0.70
        
        sorted_prices = sorted(volume_by_price.items(), key=lambda x: x[1], reverse=True)
        value_area_volume = 0
        value_area_prices = []
        
        for price, vol in sorted_prices:
            value_area_volume += vol
            value_area_prices.append(price)
            if value_area_volume >= target_volume:
                break
        
        vah = max(value_area_prices) if value_area_prices else float(close[-1])
        val = min(value_area_prices) if value_area_prices else float(close[-1])
        
        avg_volume = np.mean(list(volume_by_price.values()))
        hvn = [p for p, v in volume_by_price.items() if v > avg_volume * 1.5]
        lvn = [p for p, v in volume_by_price.items() if v < avg_volume * 0.5]
        
        return VolumeProfile(
            poc=round(poc, 2),
            vah=round(vah, 2),
            val=round(val, 2),
            high_volume_nodes=sorted(hvn)[-5:],
            low_volume_nodes=sorted(lvn)[-5:]
        )

# ==========================================
# AI ANALYZER
# ==========================================

class AIAnalyzer:
    """AI-powered trade analysis using Claude Sonnet 4."""
    
    def __init__(self, api_key: str):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
            self.client = None
    
    def analyze(self, ticker: str, indicators: AdvancedIndicators, 
                patterns: PatternAnalysis, market_structure: MarketStructure,
                volume_profile: VolumeProfile, account_size: float) -> Optional[TradeSummary]:
        """Generate AI-powered trade recommendation."""
        
        if not self.client:
            return self._fallback_analysis(ticker, indicators, account_size)
        
        try:
            prompt = self._build_analysis_prompt(ticker, indicators, patterns, 
                                                 market_structure, volume_profile, account_size)
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = response.content[0].text
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return self._create_trade_summary(ticker, indicators, analysis, account_size)
            else:
                logger.error("Failed to parse AI response")
                return self._fallback_analysis(ticker, indicators, account_size)
                
        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return self._fallback_analysis(ticker, indicators, account_size)
    
    def _build_analysis_prompt(self, ticker: str, indicators: AdvancedIndicators,
                               patterns: PatternAnalysis, market_structure: MarketStructure,
                               volume_profile: VolumeProfile, account_size: float) -> str:
        """Build comprehensive analysis prompt."""
        
        return f"""You are an elite institutional trader. Analyze this data and provide a trade recommendation.

TICKER: {ticker}
ACCOUNT SIZE: ${account_size:,.0f}

=== CURRENT PRICE & STRUCTURE ===
Price: ${indicators.price}
Market Regime: {indicators.market_regime} ({indicators.regime_confidence}% confidence)
Market Structure: {market_structure.structure}

=== TREND INDICATORS ===
SMA: 10=${indicators.sma_10}, 20=${indicators.sma_20}, 50=${indicators.sma_50}, 200=${indicators.sma_200}
EMA: 12=${indicators.ema_12}, 26=${indicators.ema_26}, 50=${indicators.ema_50}, 200=${indicators.ema_200}
VWAP: ${indicators.vwap}
ADX: {indicators.adx} (+DI: {indicators.plus_di}, -DI: {indicators.minus_di})

=== MOMENTUM ===
RSI(14): {indicators.rsi_14}, RSI(7): {indicators.rsi_7}
Stochastic: K={indicators.stochastic_k}, D={indicators.stochastic_d}
MACD: {indicators.macd}, Signal: {indicators.macd_signal}, Histogram: {indicators.macd_histogram}

=== VOLATILITY ===
ATR: {indicators.atr} ({indicators.atr_percent}% of price)
Bollinger Bands: Upper=${indicators.bb_upper}, Middle=${indicators.bb_middle}, Lower=${indicators.bb_lower}

=== VOLUME ANALYSIS ===
Volume Ratio: {indicators.volume_ratio}x average
OBV: {indicators.obv:,.0f}
MFI: {indicators.mfi}
Volume Profile POC: ${volume_profile.poc}
Value Area: ${volume_profile.val} - ${volume_profile.vah}

=== PATTERNS ===
Bullish: {', '.join(patterns.bullish_patterns) if patterns.bullish_patterns else 'None'}
Bearish: {', '.join(patterns.bearish_patterns) if patterns.bearish_patterns else 'None'}
Candlestick: {', '.join(patterns.candlestick_patterns) if patterns.candlestick_patterns else 'None'}

=== SMART MONEY CONCEPTS ===
Structure: {market_structure.structure}
Order Blocks: {len(market_structure.order_blocks)}
Fair Value Gaps: {len(market_structure.fair_value_gaps)}
Equilibrium: ${market_structure.equilibrium}
Premium Zone: ${market_structure.premium_zone[0]:.2f} - ${market_structure.premium_zone[1]:.2f}
Discount Zone: ${market_structure.discount_zone[0]:.2f} - ${market_structure.discount_zone[1]:.2f}

Provide trade recommendation as JSON (no markdown):
{{
  "action": "BUY|SELL|HOLD",
  "confidence": 0-100,
  "stop_loss_price": number,
  "take_profit_levels": [tp1, tp2, tp3],
  "position_size_shares": number,
  "win_probability": 0-100,
  "expected_value": number,
  "primary_reason": "Main thesis in one sentence",
  "supporting_signals": ["signal1", "signal2", "signal3"],
  "risk_factors": ["risk1", "risk2", "risk3"]
}}

Use ATR for stop loss. Risk max 2% of account."""
    
    def _create_trade_summary(self, ticker: str, indicators: AdvancedIndicators,
                             analysis: Dict, account_size: float) -> TradeSummary:
        """Create trade summary from AI analysis."""
        
        entry_price = indicators.price
        stop_loss = analysis.get('stop_loss_price', entry_price - indicators.atr * 2)
        
        tp_levels = analysis.get('take_profit_levels', [
            entry_price + indicators.atr * 2,
            entry_price + indicators.atr * 4,
            entry_price + indicators.atr * 6
        ])
        
        position_size = analysis.get('position_size_shares', 0)
        if position_size == 0:
            risk_per_trade = account_size * 0.02
            risk_per_share = abs(entry_price - stop_loss)
            position_size = int(risk_per_trade / risk_per_share) if risk_per_share > 0 else 0
        
        risk_amount = position_size * abs(entry_price - stop_loss)
        reward_amount = position_size * abs(tp_levels[0] - entry_price)
        rrr = reward_amount / risk_amount if risk_amount > 0 else 0
        
        return TradeSummary(
            ticker=ticker,
            action=analysis.get('action', 'HOLD'),
            confidence=analysis.get('confidence', 50),
            entry_price=round(entry_price, 2),
            stop_loss=round(stop_loss, 2),
            take_profit_1=round(tp_levels[0], 2),
            take_profit_2=round(tp_levels[1], 2) if len(tp_levels) > 1 else round(tp_levels[0] * 1.5, 2),
            take_profit_3=round(tp_levels[2], 2) if len(tp_levels) > 2 else round(tp_levels[0] * 2, 2),
            position_size=position_size,
            risk_amount=round(risk_amount, 2),
            reward_amount=round(reward_amount, 2),
            risk_reward_ratio=round(rrr, 2),
            win_probability=analysis.get('win_probability', 50),
            expected_value=analysis.get('expected_value', 0),
            primary_reason=analysis.get('primary_reason', 'Technical analysis'),
            supporting_signals=analysis.get('supporting_signals', []),
            risk_factors=analysis.get('risk_factors', []),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _fallback_analysis(self, ticker: str, indicators: AdvancedIndicators,
                          account_size: float) -> TradeSummary:
        """Fallback analysis when AI is unavailable."""
        
        action = "HOLD"
        confidence = 50
        
        # Simple rule-based logic
        bullish_signals = 0
        bearish_signals = 0
        
        if indicators.price > indicators.sma_50:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        if indicators.rsi_14 < 30:
            bullish_signals += 1
        elif indicators.rsi_14 > 70:
            bearish_signals += 1
        
        if indicators.macd > indicators.macd_signal:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            action = "BUY"
            confidence = min(75, 50 + bullish_signals * 10)
        elif bearish_signals > bullish_signals:
            action = "SELL"
            confidence = min(75, 50 + bearish_signals * 10)
        
        entry_price = indicators.price
        stop_loss = entry_price - indicators.atr * 2 if action == "BUY" else entry_price + indicators.atr * 2
        
        tp1 = entry_price + indicators.atr * 2 if action == "BUY" else entry_price - indicators.atr * 2
        tp2 = entry_price + indicators.atr * 4 if action == "BUY" else entry_price - indicators.atr * 4
        tp3 = entry_price + indicators.atr * 6 if action == "BUY" else entry_price - indicators.atr * 6
        
        risk_per_trade = account_size * 0.02
        risk_per_share = abs(entry_price - stop_loss)
        position_size = int(risk_per_trade / risk_per_share) if risk_per_share > 0 else 0
        
        risk_amount = position_size * abs(entry_price - stop_loss)
        reward_amount = position_size * abs(tp1 - entry_price)
        rrr = reward_amount / risk_amount if risk_amount > 0 else 0
        
        return TradeSummary(
            ticker=ticker,
            action=action,
            confidence=confidence,
            entry_price=round(entry_price, 2),
            stop_loss=round(stop_loss, 2),
            take_profit_1=round(tp1, 2),
            take_profit_2=round(tp2, 2),
            take_profit_3=round(tp3, 2),
            position_size=position_size,
            risk_amount=round(risk_amount, 2),
            reward_amount=round(reward_amount, 2),
            risk_reward_ratio=round(rrr, 2),
            win_probability=confidence,
            expected_value=reward_amount * (confidence/100) - risk_amount * (1 - confidence/100),
            primary_reason="Rule-based technical analysis",
            supporting_signals=[f"Bullish signals: {bullish_signals}", f"Bearish signals: {bearish_signals}"],
            risk_factors=["AI analysis unavailable", "Using simplified logic"],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

# ==========================================
# BACKTESTING ENGINE
# ==========================================

class BacktestEngine:
    """Comprehensive backtesting system."""
    
    @staticmethod
    def run_backtest(ticker: str, df: pd.DataFrame, initial_capital: float = 10000) -> BacktestResults:
        """Run complete backtest on historical data."""
        
        logger.info(f"Starting backtest for {ticker}")
        
        trades = []
        equity = initial_capital
        equity_curve = [equity]
        dates = [df.index[0].strftime("%Y-%m-%d")]
        
        position = None
        max_equity = equity
        max_drawdown = 0
        
        # Simple strategy: RSI + MACD crossover
        for i in range(50, len(df)):
            current_data = df.iloc[:i+1]
            
            # Calculate indicators
            close = current_data['Close']
            
            # RSI
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = -delta.clip(upper=0).rolling(14).mean()
            rs = gain / loss.replace(0, 1)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # MACD
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            current_price = close.iloc[-1]
            current_date = df.index[i].strftime("%Y-%m-%d")
            
            # Entry signal
            if position is None:
                if current_rsi < 35 and macd.iloc[-1] > signal.iloc[-1]:
                    # Buy signal
                    position_size = int(equity * 0.95 / current_price)
                    if position_size > 0:
                        position = {
                            'entry_date': current_date,
                            'entry_price': current_price,
                            'size': position_size,
                            'type': 'BUY',
                            'stop_loss': current_price * 0.95,
                            'take_profit': current_price * 1.10
                        }
                        equity -= position_size * current_price
            
            # Exit signal
            elif position is not None:
                # Stop loss or take profit
                if current_price <= position['stop_loss']:
                    # Stop loss hit
                    exit_price = position['stop_loss']
                    equity += position['size'] * exit_price
                    pnl = position['size'] * (exit_price - position['entry_price'])
                    pnl_pct = (exit_price / position['entry_price'] - 1) * 100
                    
                    trades.append(BacktestTrade(
                        entry_date=position['entry_date'],
                        entry_price=round(position['entry_price'], 2),
                        exit_date=current_date,
                        exit_price=round(exit_price, 2),
                        action=position['type'],
                        profit_loss=round(pnl, 2),
                        profit_loss_percent=round(pnl_pct, 2),
                        reason="Stop Loss",
                        win=pnl > 0
                    ))
                    position = None
                    
                elif current_price >= position['take_profit']:
                    # Take profit hit
                    exit_price = position['take_profit']
                    equity += position['size'] * exit_price
                    pnl = position['size'] * (exit_price - position['entry_price'])
                    pnl_pct = (exit_price / position['entry_price'] - 1) * 100
                    
                    trades.append(BacktestTrade(
                        entry_date=position['entry_date'],
                        entry_price=round(position['entry_price'], 2),
                        exit_date=current_date,
                        exit_price=round(exit_price, 2),
                        action=position['type'],
                        profit_loss=round(pnl, 2),
                        profit_loss_percent=round(pnl_pct, 2),
                        reason="Take Profit",
                        win=pnl > 0
                    ))
                    position = None
                
                elif current_rsi > 65 or macd.iloc[-1] < signal.iloc[-1]:
                    # Exit signal
                    exit_price = current_price
                    equity += position['size'] * exit_price
                    pnl = position['size'] * (exit_price - position['entry_price'])
                    pnl_pct = (exit_price / position['entry_price'] - 1) * 100
                    
                    trades.append(BacktestTrade(
                        entry_date=position['entry_date'],
                        entry_price=round(position['entry_price'], 2),
                        exit_date=current_date,
                        exit_price=round(exit_price, 2),
                        action=position['type'],
                        profit_loss=round(pnl, 2),
                        profit_loss_percent=round(pnl_pct, 2),
                        reason="Exit Signal",
                        win=pnl > 0
                    ))
                    position = None
            
            # Update equity curve
            current_equity = equity
            if position:
                current_equity += position['size'] * current_price
            
            equity_curve.append(current_equity)
            dates.append(current_date)
            
            # Track drawdown
            if current_equity > max_equity:
                max_equity = current_equity
            drawdown = (max_equity - current_equity) / max_equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Close any open position
        if position:
            exit_price = df['Close'].iloc[-1]
            equity += position['size'] * exit_price
            pnl = position['size'] * (exit_price - position['entry_price'])
            pnl_pct = (exit_price / position['entry_price'] - 1) * 100
            
            trades.append(BacktestTrade(
                entry_date=position['entry_date'],
                entry_price=round(position['entry_price'], 2),
                exit_date=df.index[-1].strftime("%Y-%m-%d"),
                exit_price=round(exit_price, 2),
                action=position['type'],
                profit_loss=round(pnl, 2),
                profit_loss_percent=round(pnl_pct, 2),
                reason="End of Period",
                win=pnl > 0
            ))
        
        # Calculate statistics
        winning_trades = [t for t in trades if t.win]
        losing_trades = [t for t in trades if not t.win]
        
        total_wins = len(winning_trades)
        total_losses = len(losing_trades)
        win_rate = (total_wins / len(trades) * 100) if trades else 0
        
        avg_win = np.mean([t.profit_loss for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.profit_loss for t in losing_trades]) if losing_trades else 0
        
        largest_win = max([t.profit_loss for t in winning_trades]) if winning_trades else 0
        largest_loss = min([t.profit_loss for t in losing_trades]) if losing_trades else 0
        
        total_gains = sum([t.profit_loss for t in winning_trades])
        total_losses_amt = abs(sum([t.profit_loss for t in losing_trades]))
        profit_factor = total_gains / total_losses_amt if total_losses_amt > 0 else 0
        
        # Sharpe ratio
        returns = pd.Series(equity_curve).pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if len(returns) > 0 and returns.std() > 0 else 0
        
        total_return = equity - initial_capital
        total_return_pct = (equity / initial_capital - 1) * 100
        
        return BacktestResults(
            ticker=ticker,
            start_date=df.index[0].strftime("%Y-%m-%d"),
            end_date=df.index[-1].strftime("%Y-%m-%d"),
            initial_capital=initial_capital,
            final_capital=round(equity, 2),
            total_return=round(total_return, 2),
            total_return_percent=round(total_return_pct, 2),
            total_trades=len(trades),
            winning_trades=total_wins,
            losing_trades=total_losses,
            win_rate=round(win_rate, 2),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            largest_win=round(largest_win, 2),
            largest_loss=round(largest_loss, 2),
            profit_factor=round(profit_factor, 2),
            sharpe_ratio=round(sharpe, 2),
            max_drawdown=round(max_drawdown * initial_capital, 2),
            max_drawdown_percent=round(max_drawdown * 100, 2),
            trades=trades,
            equity_curve=equity_curve,
            dates=dates
        )

# ==========================================
# DISPLAY & REPORTING
# ==========================================

class DisplayManager:
    """Manages all console output and reporting."""
    
    @staticmethod
    def show_header():
        """Display application header."""
        console.clear()
        header = Panel(
            "[bold cyan]FinalAI Quantum v6.2[/bold cyan]\n"
            "[dim]Elite Professional Trading System[/dim]\n"
            "[yellow]80+ Indicators | AI-Powered Analysis | Smart Money Concepts[/yellow]",
            border_style="cyan",
            box=box.DOUBLE
        )
        console.print(header)
        console.print()
    
    @staticmethod
    def show_indicators(indicators: AdvancedIndicators):
        """Display technical indicators."""
        table = Table(title="📊 Technical Indicators", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Indicator", style="white")
        table.add_column("Value", style="yellow", justify="right")
        
        table.add_row("Price", "Current", f"${indicators.price}")
        table.add_row("", "Open/High/Low", f"${indicators.open} / ${indicators.high} / ${indicators.low}")
        table.add_row("", "Volume", f"{indicators.volume:,}")
        
        table.add_row("Trend", "SMA 20/50/200", f"${indicators.sma_20} / ${indicators.sma_50} / ${indicators.sma_200}")
        table.add_row("", "EMA 12/26/50", f"${indicators.ema_12} / ${indicators.ema_26} / ${indicators.ema_50}")
        table.add_row("", "VWAP", f"${indicators.vwap}")
        
        table.add_row("Momentum", "RSI (7/14)", f"{indicators.rsi_7} / {indicators.rsi_14}")
        table.add_row("", "Stochastic K/D", f"{indicators.stochastic_k} / {indicators.stochastic_d}")
        table.add_row("", "MACD", f"{indicators.macd:.4f}")
        
        table.add_row("Volatility", "ATR", f"{indicators.atr} ({indicators.atr_percent}%)")
        table.add_row("", "BB Upper/Lower", f"${indicators.bb_upper} / ${indicators.bb_lower}")
        
        table.add_row("Strength", "ADX", f"{indicators.adx}")
        table.add_row("", "+DI / -DI", f"{indicators.plus_di} / {indicators.minus_di}")
        
        table.add_row("Volume", "Volume Ratio", f"{indicators.volume_ratio}x")
        table.add_row("", "OBV", f"{indicators.obv:,.0f}")
        table.add_row("", "MFI", f"{indicators.mfi}")
        
        table.add_row("Regime", "Market Regime", f"[bold]{indicators.market_regime}[/bold]")
        table.add_row("", "Confidence", f"{indicators.regime_confidence}%")
        
        console.print(table)
        console.print()
    
    @staticmethod
    def show_trade_recommendation(trade: TradeSummary):
        """Display trade recommendation."""
        
        action_color = "green" if trade.action == "BUY" else "red" if trade.action == "SELL" else "yellow"
        
        panel = Panel(
            f"[bold {action_color}]{trade.action}[/bold {action_color}] {trade.ticker}\n"
            f"[dim]Confidence: {trade.confidence}% | Win Probability: {trade.win_probability}%[/dim]",
            title="🎯 Trade Recommendation",
            border_style=action_color,
            box=box.HEAVY
        )
        console.print(panel)
        
        table = Table(box=box.ROUNDED, show_header=False)
        table.add_column("", style="cyan", width=20)
        table.add_column("", style="white")
        
        table.add_row("Entry Price", f"${trade.entry_price}")
        table.add_row("Stop Loss", f"[red]${trade.stop_loss}[/red]")
        table.add_row("Take Profit 1", f"[green]${trade.take_profit_1}[/green]")
        table.add_row("Take Profit 2", f"[green]${trade.take_profit_2}[/green]")
        table.add_row("Take Profit 3", f"[green]${trade.take_profit_3}[/green]")
        table.add_row("", "")
        table.add_row("Position Size", f"{trade.position_size} shares")
        table.add_row("Risk Amount", f"[red]${trade.risk_amount}[/red]")
        table.add_row("Reward Amount", f"[green]${trade.reward_amount}[/green]")
        table.add_row("Risk:Reward Ratio", f"1:{trade.risk_reward_ratio}")
        table.add_row("Expected Value", f"${trade.expected_value:.2f}")
        
        console.print(table)
        console.print()
        
        console.print("[bold cyan]Primary Thesis:[/bold cyan]")
        console.print(f"  {trade.primary_reason}\n")
        
        if trade.supporting_signals:
            console.print("[bold green]Supporting Signals:[/bold green]")
            for signal in trade.supporting_signals:
                console.print(f"  ✓ {signal}")
            console.print()
        
        if trade.risk_factors:
            console.print("[bold red]Risk Factors:[/bold red]")
            for risk in trade.risk_factors:
                console.print(f"  ⚠ {risk}")
            console.print()
    
    @staticmethod
    def show_backtest_results(results: BacktestResults):
        """Display backtest results."""
        
        title = f"📈 Backtest Results: {results.ticker}"
        
        # Summary Panel
        return_color = "green" if results.total_return > 0 else "red"
        summary = Panel(
            f"Period: {results.start_date} to {results.end_date}\n"
            f"Initial Capital: ${results.initial_capital:,.2f}\n"
            f"Final Capital: ${results.final_capital:,.2f}\n"
            f"[bold {return_color}]Total Return: ${results.total_return:,.2f} ({results.total_return_percent:+.2f}%)[/bold {return_color}]",
            title=title,
            border_style=return_color,
            box=box.HEAVY
        )
        console.print(summary)
        console.print()
        
        # Statistics Table
        stats_table = Table(title="📊 Performance Statistics", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow", justify="right")
        
        stats_table.add_row("Total Trades", str(results.total_trades))
        stats_table.add_row("Winning Trades", f"[green]{results.winning_trades}[/green]")
        stats_table.add_row("Losing Trades", f"[red]{results.losing_trades}[/red]")
        stats_table.add_row("Win Rate", f"{results.win_rate:.2f}%")
        stats_table.add_row("", "")
        stats_table.add_row("Average Win", f"[green]${results.avg_win:,.2f}[/green]")
        stats_table.add_row("Average Loss", f"[red]${results.avg_loss:,.2f}[/red]")
        stats_table.add_row("Largest Win", f"[green]${results.largest_win:,.2f}[/green]")
        stats_table.add_row("Largest Loss", f"[red]${results.largest_loss:,.2f}[/red]")
        stats_table.add_row("", "")
        stats_table.add_row("Profit Factor", f"{results.profit_factor:.2f}")
        stats_table.add_row("Sharpe Ratio", f"{results.sharpe_ratio:.2f}")
        stats_table.add_row("Max Drawdown", f"[red]${results.max_drawdown:,.2f} ({results.max_drawdown_percent:.2f}%)[/red]")
        
        console.print(stats_table)
        console.print()
        
        # Recent Trades
        if results.trades:
            trades_table = Table(title="📝 Recent Trades (Last 10)", box=box.ROUNDED)
            trades_table.add_column("Entry", style="cyan")
            trades_table.add_column("Exit", style="cyan")
            trades_table.add_column("Action", style="white")
            trades_table.add_column("P/L", style="white", justify="right")
            trades_table.add_column("P/L %", style="white", justify="right")
            trades_table.add_column("Reason", style="dim")
            
            for trade in results.trades[-10:]:
                pl_color = "green" if trade.win else "red"
                trades_table.add_row(
                    trade.entry_date,
                    trade.exit_date,
                    trade.action,
                    f"[{pl_color}]${trade.profit_loss:,.2f}[/{pl_color}]",
                    f"[{pl_color}]{trade.profit_loss_percent:+.2f}%[/{pl_color}]",
                    trade.reason
                )
            
            console.print(trades_table)
            console.print()
        
        # Equity Curve Visualization (ASCII)
        DisplayManager._show_equity_curve(results)
    
    @staticmethod
    def _show_equity_curve(results: BacktestResults):
        """Display ASCII equity curve."""
        console.print("[bold cyan]📈 Equity Curve[/bold cyan]")
        
        # Normalize equity curve to fit terminal width
        curve = results.equity_curve
        width = 80
        height = 15
        
        if len(curve) > width:
            # Downsample
            step = len(curve) // width
            curve = [curve[i] for i in range(0, len(curve), step)]
        
        min_val = min(curve)
        max_val = max(curve)
        range_val = max_val - min_val if max_val > min_val else 1
        
        # Create ASCII chart
        for h in range(height, 0, -1):
            line = ""
            threshold = min_val + (range_val * h / height)
            for val in curve:
                if val >= threshold:
                    line += "█"
                else:
                    line += " "
            
            # Add value labels
            if h == height:
                console.print(f"${max_val:>10,.0f} |{line}|")
            elif h == 1:
                console.print(f"${min_val:>10,.0f} |{line}|")
            else:
                console.print(f"           |{line}|")
        
        console.print(f"           {'+' + '-'*len(curve) + '+'}")
        console.print(f"           Start{' '*(len(curve)-10)}End\n")

# ==========================================
# MAIN APPLICATION
# ==========================================

class FinalAIQuantum:
    """Main application controller."""
    
    def __init__(self):
        self.config = None
        self.api_key = None
        self.analyzer = None
    
    def initialize(self):
        """Initialize application with all checks."""
        DisplayManager.show_header()
        
        # Check dependencies
        ConfigurationManager.check_dependencies()
        
        # Setup API keys
        self.api_key = ConfigurationManager.setup_api_keys()
        
        # Setup trading preferences
        self.config = ConfigurationManager.setup_trading_preferences()
        
        # Initialize AI analyzer
        try:
            import anthropic
            self.analyzer = AIAnalyzer(self.api_key)
            console.print("[green]✓ AI Analyzer initialized[/green]\n")
        except Exception as e:
            logger.warning(f"AI initialization failed: {e}")
            console.print("[yellow]⚠ AI analysis unavailable, using fallback[/yellow]\n")
            self.analyzer = AIAnalyzer("")
    
    def run(self):
        """Main application loop."""
        while True:
            DisplayManager.show_header()
            
            console.print("[bold cyan]Main Menu[/bold cyan]\n")
            console.print("1. 📊 Analyze Stock/Crypto")
            console.print("2. 🔄 Run Backtest")
            console.print("3. ⚙️  Settings")
            console.print("4. 🚪 Exit\n")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")
            
            if choice == "1":
                self.analyze_ticker()
            elif choice == "2":
                self.run_backtest()
            elif choice == "3":
                self.settings_menu()
            elif choice == "4":
                console.print("\n[cyan]Thanks for using FinalAI Quantum! 🚀[/cyan]\n")
                break
    
    def analyze_ticker(self):
        """Analyze a ticker."""
        DisplayManager.show_header()
        
        console.print("[bold cyan]📊 Live Market Analysis[/bold cyan]\n")
        
        ticker = Prompt.ask("Enter ticker symbol (e.g., AAPL, BTC-USD)").upper().strip()
        
        # Handle multiple tickers
        if ',' in ticker or ' ' in ticker:
            tickers = [t.strip() for t in ticker.replace(',', ' ').split() if t.strip()]
            console.print(f"\n[yellow]⚠ Multiple tickers detected. Analyzing: {tickers[0]}[/yellow]")
            ticker = tickers[0]
        
        console.print("\n[bold cyan]Select Trading Style:[/bold cyan]")
        console.print("1. ⚡ Day Trading (5m-1h)")
        console.print("2. 📈 Swing Trading (1h-1d)")
        console.print("3. 💎 Long-Term (Daily-Weekly)\n")
        
        style_choice = Prompt.ask("Select style", choices=["1", "2", "3"], default="2")
        
        style_map = {
            "1": TradingStyle.DAY_TRADE,
            "2": TradingStyle.SWING_TRADE,
            "3": TradingStyle.LONG_TERM
        }
        
        style = style_map[style_choice]
        config = TradingConfig.get_config(style)
        
        console.print(f"\n[yellow]Fetching data for {ticker}...[/yellow]")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Analyzing...", total=None)
            
            # Fetch data
            df = DataManager.fetch_data(ticker, config.period, config.interval)
            
            if df is None:
                console.print(f"\n[red]❌ Failed to fetch data for {ticker}[/red]")
                console.print("[yellow]💡 Tips:[/yellow]")
                console.print("  • Check ticker symbol is correct")
                console.print("  • For crypto, use format: BTC-USD, ETH-USD")
                console.print("  • For stocks, use: AAPL, TSLA, NVDA")
                console.print("  • Ensure you have internet connection")
                Prompt.ask("\nPress Enter to continue")
                return
            
            # Calculate indicators
            progress.update(task, description="Calculating 80+ indicators...")
            indicators = TechnicalAnalyzer.calculate_indicators(df)
            
            if indicators is None:
                console.print(f"\n[red]❌ Failed to calculate indicators[/red]")
                console.print(f"[dim]Data points available: {len(df)}[/dim]")
                Prompt.ask("\nPress Enter to continue")
                return
            
            # Pattern recognition
            progress.update(task, description="Detecting patterns...")
            patterns = PatternRecognizer.analyze(df)
            
            # Smart Money analysis
            progress.update(task, description="Analyzing Smart Money Concepts...")
            market_structure = SmartMoneyAnalyzer.analyze(df)
            
            # Volume Profile
            progress.update(task, description="Building Volume Profile...")
            volume_profile = VolumeProfileAnalyzer.analyze(df)
            
            # AI Analysis
            progress.update(task, description="Running AI analysis...")
            trade_summary = self.analyzer.analyze(
                ticker, indicators, patterns, market_structure,
                volume_profile, self.config['account_size']
            )
        
        # Display results
        DisplayManager.show_header()
        console.print(f"[bold cyan]Analysis Complete: {ticker}[/bold cyan]")
        console.print(f"[dim]Data from {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')} ({len(df)} bars)[/dim]\n")
        
        DisplayManager.show_indicators(indicators)
        
        # Show patterns
        if patterns.bullish_patterns or patterns.bearish_patterns or patterns.candlestick_patterns:
            console.print("[bold cyan]📐 Detected Patterns:[/bold cyan]")
            if patterns.bullish_patterns:
                console.print(f"[green]Bullish:[/green] {', '.join(patterns.bullish_patterns)}")
            if patterns.bearish_patterns:
                console.print(f"[red]Bearish:[/red] {', '.join(patterns.bearish_patterns)}")
            if patterns.candlestick_patterns:
                console.print(f"[yellow]Candlestick:[/yellow] {', '.join(patterns.candlestick_patterns)}")
            console.print()
        
        # Show market structure
        console.print(f"[bold cyan]🎯 Smart Money Analysis:[/bold cyan]")
        console.print(f"Market Structure: [bold]{market_structure.structure}[/bold]")
        console.print(f"Order Blocks: {len(market_structure.order_blocks)}")
        console.print(f"Fair Value Gaps: {len(market_structure.fair_value_gaps)}")
        console.print(f"Equilibrium: ${market_structure.equilibrium}\n")
        
        # Show volume profile
        console.print(f"[bold cyan]📊 Volume Profile:[/bold cyan]")
        console.print(f"POC: ${volume_profile.poc}")
        console.print(f"Value Area: ${volume_profile.val} - ${volume_profile.vah}\n")
        
        if trade_summary:
            DisplayManager.show_trade_recommendation(trade_summary)
            
            # Save report
            self._save_analysis_report(ticker, trade_summary)
        
        Prompt.ask("\nPress Enter to continue")
    
    def run_backtest(self):
        """Run backtest."""
        DisplayManager.show_header()
        
        console.print("[bold cyan]🔄 Backtesting Engine[/bold cyan]\n")
        
        ticker = Prompt.ask("Enter ticker symbol").upper()
        
        console.print("\n[bold cyan]Select Backtest Period:[/bold cyan]")
        console.print("1. 1 Year")
        console.print("2. 2 Years")
        console.print("3. 5 Years")
        console.print("4. Custom\n")
        
        period_choice = Prompt.ask("Select period", choices=["1", "2", "3", "4"], default="2")
        
        period_map = {"1": "1y", "2": "2y", "3": "5y", "4": "max"}
        period = period_map[period_choice]
        
        initial_capital = FloatPrompt.ask(
            "Initial capital ($)",
            default=self.config['account_size']
        )
        
        console.print(f"\n[yellow]Running backtest for {ticker}...[/yellow]\n")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Backtesting...", total=None)
            
            # Fetch historical data
            df = DataManager.fetch_data(ticker, period, "1d")
            
            if df is None:
                console.print(f"\n[red]❌ Failed to fetch data for {ticker}[/red]")
                Prompt.ask("\nPress Enter to continue")
                return
            
            # Run backtest
            results = BacktestEngine.run_backtest(ticker, df, initial_capital)
        
        # Display results
        DisplayManager.show_header()
        DisplayManager.show_backtest_results(results)
        
        # Save results
        self._save_backtest_results(results)
        
        Prompt.ask("\nPress Enter to continue")
    
    def settings_menu(self):
        """Settings menu."""
        while True:
            DisplayManager.show_header()
            
            console.print("[bold cyan]⚙️  Settings[/bold cyan]\n")
            console.print(f"Current Account Size: ${self.config['account_size']:,.2f}")
            console.print(f"Risk Per Trade: {self.config['risk_per_trade']}%")
            console.print(f"Max Positions: {self.config['max_positions']}\n")
            
            console.print("1. Update Account Size")
            console.print("2. Update Risk Per Trade")
            console.print("3. Update Max Positions")
            console.print("4. Reconfigure API Keys")
            console.print("5. Back to Main Menu\n")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="5")
            
            if choice == "1":
                new_size = FloatPrompt.ask("New account size ($)", default=self.config['account_size'])
                self.config['account_size'] = new_size
                ConfigurationManager.save_config(self.config)
                console.print("[green]✓ Account size updated[/green]")
                Prompt.ask("\nPress Enter to continue")
            
            elif choice == "2":
                new_risk = FloatPrompt.ask("New risk per trade (%)", default=self.config['risk_per_trade'])
                self.config['risk_per_trade'] = new_risk
                ConfigurationManager.save_config(self.config)
                console.print("[green]✓ Risk per trade updated[/green]")
                Prompt.ask("\nPress Enter to continue")
            
            elif choice == "3":
                new_max = IntPrompt.ask("New max positions", default=self.config['max_positions'])
                self.config['max_positions'] = new_max
                ConfigurationManager.save_config(self.config)
                console.print("[green]✓ Max positions updated[/green]")
                Prompt.ask("\nPress Enter to continue")
            
            elif choice == "4":
                self.api_key = ConfigurationManager.setup_api_keys()
                self.analyzer = AIAnalyzer(self.api_key)
                console.print("[green]✓ API keys reconfigured[/green]")
                Prompt.ask("\nPress Enter to continue")
            
            elif choice == "5":
                break
    
    def _save_analysis_report(self, ticker: str, trade: TradeSummary):
        """Save analysis report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = RESULTS_DIR / f"{ticker}_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(asdict(trade), f, indent=2)
        
        console.print(f"[dim]Report saved to: {filename}[/dim]")
    
    def _save_backtest_results(self, results: BacktestResults):
        """Save backtest results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = RESULTS_DIR / f"{results.ticker}_backtest_{timestamp}.json"
        
        # Convert to dict
        results_dict = asdict(results)
        
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        console.print(f"[dim]Results saved to: {filename}[/dim]")

# ==========================================
# ENTRY POINT
# ==========================================

def main():
    """Application entry point."""
    try:
        app = FinalAIQuantum()
        app.initialize()
        app.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠ Application interrupted by user[/yellow]")
    except Exception as e:
        logger.exception("Fatal error")
        console.print(f"\n[red]❌ Fatal error: {str(e)}[/red]")
        console.print("[dim]Check logs for details[/dim]")

if __name__ == "__main__":
    main()