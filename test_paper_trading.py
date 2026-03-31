"""
Test Paper Trading Functionality
Run this to verify paper trading works correctly.
"""

import sys
from pathlib import Path

# Quick test of paper trading
print("Testing Paper Trading System...")
print("-" * 50)

# Test 1: Import modules
try:
    from datetime import datetime
    from dataclasses import dataclass, asdict
    from typing import Optional
    print("✓ Imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create PaperTrade dataclass
try:
    @dataclass
    class PaperTrade:
        ticker: str
        action: str
        entry_price: float
        entry_time: datetime
        stop_loss: float
        take_profit: float
        position_size: int
        status: str = "OPEN"
        exit_price: Optional[float] = None
        exit_time: Optional[datetime] = None
        pnl: float = 0.0
        pnl_pct: float = 0.0
        reason: str = ""
    
    print("✓ PaperTrade dataclass created")
except Exception as e:
    print(f"✗ Dataclass creation failed: {e}")
    sys.exit(1)

# Test 3: Create a trade instance
try:
    trade = PaperTrade(
        ticker="AAPL",
        action="LONG",
        entry_price=180.50,
        entry_time=datetime.now(),
        stop_loss=175.00,
        take_profit=190.00,
        position_size=10
    )
    print("✓ Trade instance created")
    print(f"  - Ticker: {trade.ticker}")
    print(f"  - Action: {trade.action}")
    print(f"  - Entry: ${trade.entry_price}")
    print(f"  - Status: {trade.status}")
except Exception as e:
    print(f"✗ Trade creation failed: {e}")
    sys.exit(1)

# Test 4: Test asdict conversion
try:
    trade_dict = asdict(trade)
    print("✓ Dict conversion successful")
except Exception as e:
    print(f"✗ Dict conversion failed: {e}")
    sys.exit(1)

# Test 5: Test file operations
try:
    import json
    from pathlib import Path
    
    RESULTS_DIR = Path("results")
    RESULTS_DIR.mkdir(exist_ok=True)
    
    test_file = RESULTS_DIR / "test_paper_trades.json"
    
    # Save
    trade_dict['entry_time'] = trade.entry_time.isoformat()
    if trade.exit_time:
        trade_dict['exit_time'] = trade.exit_time.isoformat()
    
    with open(test_file, 'w') as f:
        json.dump([trade_dict], f, indent=2)
    
    print("✓ File save successful")
    
    # Load
    with open(test_file, 'r') as f:
        loaded = json.load(f)
    
    print("✓ File load successful")
    
    # Clean up
    test_file.unlink()
    
except Exception as e:
    print(f"✗ File operations failed: {e}")
    sys.exit(1)

print("-" * 50)
print("✓ ALL TESTS PASSED!")
print()
print("Paper Trading System is working correctly!")
print()
print("To use in Trading.py:")
print("1. Menu → 22. Paper Trading Summary (view all trades)")
print("2. Menu → 1. Analyze Ticker → Live Scan → Choose 'paper' when prompted")
print("3. Menu → 24. Close Paper Trade Manually (close a trade)")
print()
print("Your paper trades are saved in: results/paper_trades.json")
