import sys
sys.path.insert(0, 'C:/Users/aravn')

from ai import WatchlistManager

wm = WatchlistManager()

# Add some stocks to watch
wm.add_asset("my_stocks", "AAPL", "stock", "short-term")
wm.add_asset("my_stocks", "MSFT", "stock", "short-term")
wm.add_asset("my_stocks", "TSLA", "stock", "short-term")
wm.add_asset("my_stocks", "NVDA", "stock", "short-term")

print("✅ Watchlist created with 4 stocks!")
print("Watchlists:", wm.list_watchlists())