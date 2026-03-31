"""Alpaca streaming adapter.

This adapter tries to use `alpaca-py` StreamingClient if available, falling back to
`alpaca_trade_api` streaming interfaces if not. It keeps an in-memory ring buffer
of recent ticks and offers `get_recent_ohlcv(resample='1S', limit=300)` for the
live scanners in `Trading.py`.

Notes:
- Requires Alpaca API keys configured in `.env` (see `ConfigurationManager.setup_api_keys`).
- Streaming requires network access and appropriate market-data entitlements on Alpaca.
"""
import asyncio
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

try:
    # prefer alpaca-py (modern client)
    from alpaca.data.stream import Stream as AlpacaPyStream
    from alpaca.trading.stream import TradingStream
    HAS_ALPACA_PY = True
except Exception:
    HAS_ALPACA_PY = False

try:
    import alpaca_trade_api as tradeapi
    HAS_ALPACA_TRADEAPI = True
except Exception:
    HAS_ALPACA_TRADEAPI = False

from Trading import ConfigurationManager


class AlpacaStreamingAdapter:
    """Provides a lightweight streaming adapter for ticks and aggregated bars."""

    def __init__(self, symbols=None):
        self.symbols = symbols or []
        self.ticks = {s: deque(maxlen=10000) for s in self.symbols}
        self.lock = threading.Lock()
        self._loop = None
        self._stream = None
        self._thread = None

        # ensure keys exist
        self._ensure_keys()

    def _ensure_keys(self):
        env = Path('.env')
        if not env.exists():
            ConfigurationManager.setup_api_keys()

    def start(self):
        # start streaming in background thread
        if HAS_ALPACA_PY:
            self._thread = threading.Thread(target=self._run_alpaca_py, daemon=True)
            self._thread.start()
        elif HAS_ALPACA_TRADEAPI:
            # tradeapi streaming could be implemented here (omitted for brevity)
            raise RuntimeError('alpaca_trade_api streaming not implemented in this adapter')
        else:
            raise RuntimeError('No Alpaca streaming client installed (install alpaca-py)')

    def _run_alpaca_py(self):
        # lazy import inside thread
        try:
            from alpaca.data import API
            from alpaca.data.stream import Stream
        except Exception as e:
            print('Failed to import alpaca-py streaming:', e)
            return

        # pull credentials from .env
        env = Path('.env')
        keys = {}
        if env.exists():
            with open(env, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        k, v = line.strip().split('=', 1)
                        keys[k] = v.strip('\"').strip("'\")

        api_key = keys.get('ALPACA_API_KEY')
        api_secret = keys.get('ALPACA_SECRET_KEY')
        base = keys.get('ALPACA_BASE', 'paper')

        # Setup stream
        try:
            stream = Stream(api_key=api_key, api_secret=api_secret, base_url='https://paper-api.alpaca.markets')
        except Exception:
            try:
                stream = Stream(api_key=api_key, api_secret=api_secret)
            except Exception as e:
                print('Failed to create Alpaca Stream:', e)
                return

        async def handle_trade(t):
            symbol = t.symbol
            price = float(t.price)
            qty = float(t.size)
            ts = datetime.utcfromtimestamp(t.timestamp / 1000.0) if isinstance(t.timestamp, (int,float)) else datetime.utcnow()
            with self.lock:
                if symbol not in self.ticks:
                    self.ticks[symbol] = deque(maxlen=10000)
                self.ticks[symbol].append({'price': price, 'qty': qty, 'ts': ts})

        for s in self.symbols:
            try:
                stream.subscribe_trades(handle_trade, s)
            except Exception:
                # try uppercase
                stream.subscribe_trades(handle_trade, s.upper())

        self._stream = stream
        try:
            stream.run()
        except Exception as e:
            print('Alpaca stream run ended:', e)

    def subscribe(self, symbol: str):
        with self.lock:
            if symbol not in self.ticks:
                self.ticks[symbol] = deque(maxlen=10000)
            if symbol not in self.symbols:
                self.symbols.append(symbol)

    def get_recent_ohlcv(self, symbol: str, resample: str = '1S', limit: int = 300) -> pd.DataFrame:
        """Return recent OHLCV aggregated to `resample` (pandas offset alias)."""
        with self.lock:
            data = list(self.ticks.get(symbol, []))
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df = df.set_index(pd.DatetimeIndex(df['ts']))
        df = df.resample(resample).agg({'price': ['first','max','min','last'], 'qty': 'sum'})
        # Flatten columns
        df.columns = ['_'.join(col).strip() for col in df.columns.values]
        df = df.rename(columns={'price_first':'Open','price_max':'High','price_min':'Low','price_last':'Close','qty_sum':'Volume'})
        df = df.dropna()
        if len(df) > limit:
            return df.iloc[-limit:]
        return df
