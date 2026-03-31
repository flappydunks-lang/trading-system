"""
Alpaca REST adapter for live bar data.
Uses Alpaca v2 API with get_bars() instead of deprecated get_barset().
"""

import os
from datetime import datetime, timedelta
import pandas as pd

try:
    from alpaca_trade_api import REST
except ImportError:
    REST = None


class AlpacaLiveAdapter:
    """Fetch live 1-min bars from Alpaca with fallback error handling."""
    
    def __init__(self):
        """Initialize Alpaca REST client from environment."""
        api_key = os.getenv('APCA_API_KEY_ID')
        secret_key = os.getenv('APCA_API_SECRET_KEY')
        base_url = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not secret_key:
            raise ValueError('Alpaca API keys not found in environment (.env file)')
        
        if REST is None:
            raise ValueError('alpaca_trade_api not installed')
        
        self.api = REST(api_key, secret_key, base_url, api_version='v2')
    
    def get_latest_bars(self, symbol: str, timeframe: str = '1Min', limit: int = 120) -> pd.DataFrame:
        """
        Fetch latest bars using Alpaca v2 API.
        
        Args:
            symbol (str): Ticker symbol (e.g., 'ES', 'AAPL')
            timeframe (str): Bar timeframe ('1Min', '5Min', '15Min', '1H', '1D')
            limit (int): Number of bars to fetch (max 10000)
        
        Returns:
            pd.DataFrame: DataFrame with Open, High, Low, Close, Volume, Timestamp
        """
        try:
            # Convert '1Min' to Alpaca's '1' format for 1-minute bars
            alpaca_timeframe = self._convert_timeframe(timeframe)
            
            # Calculate start time (go back enough to get limit bars)
            end_time = datetime.utcnow()
            if alpaca_timeframe == '1':  # 1 minute
                start_time = end_time - timedelta(minutes=limit + 10)
            elif alpaca_timeframe == '5':  # 5 minutes
                start_time = end_time - timedelta(minutes=limit * 5 + 50)
            elif alpaca_timeframe == '15':  # 15 minutes
                start_time = end_time - timedelta(minutes=limit * 15 + 150)
            elif alpaca_timeframe == '1H':  # 1 hour
                start_time = end_time - timedelta(hours=limit + 10)
            else:
                start_time = end_time - timedelta(days=limit + 10)
            
            # Fetch bars from Alpaca v2 API - try modern API first
            bars = None
            try:
                # Try new API format (alpaca-trade-api >= 2.0)
                bars = self.api.get_bars(
                    symbol,
                    alpaca_timeframe,
                    start=start_time,
                    end=end_time,
                    limit=limit
                )
            except (TypeError, AttributeError):
                # Fallback for older alpaca-trade-api versions
                try:
                    bars = self.api.get_bars(
                        symbol,
                        alpaca_timeframe,
                        start=start_time.isoformat(),
                        end=end_time.isoformat(),
                        limit=limit
                    )
                except Exception as e2:
                    raise Exception(f'Both API formats failed: {str(e2)[:60]}')
            
            if not bars or len(bars) == 0:
                return None
            
            # Convert to DataFrame
            df = self._bars_to_dataframe(bars)
            
            # Keep only the last `limit` bars
            df = df.tail(limit)
            
            return df
        
        except Exception as e:
            raise Exception(f'Alpaca bars fetch: {str(e)[:80]}')
    
    def _convert_timeframe(self, timeframe_str):
        """Convert timeframe string to Alpaca format."""
        mapping = {
            '1Min': '1',
            '5Min': '5',
            '15Min': '15',
            '1H': '1H',
            '1D': '1D',
            '1': '1',
            '5': '5',
            '15': '15',
        }
        return mapping.get(timeframe_str, '1')
    
    def _bars_to_dataframe(self, bars):
        """Convert Alpaca bars object to pandas DataFrame."""
        rows = []
        for bar in bars:
            rows.append({
                'Open': bar.o,
                'High': bar.h,
                'Low': bar.l,
                'Close': bar.c,
                'Volume': bar.v,
                'Timestamp': bar.t,
            })
        
        df = pd.DataFrame(rows)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df.set_index('Timestamp', inplace=True)
        df = df.sort_index()
                    'c': b.c,
                    'v': b.v
                } for b in barset[symbol]])
                if df.empty:
                    return None
                df['t'] = pd.to_datetime(df['t'])
                df = df.set_index('t')
                return df
            except Exception as e:
                raise RuntimeError(f"Failed to fetch bars from Alpaca: {e}")