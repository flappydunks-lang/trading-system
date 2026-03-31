"""
Test Menu Option 23 - Run Quantitative Strategies
This simulates running the quant strategies without full app initialization
"""

import sys
import os

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Testing Menu Option 23: Run Quantitative Strategies")
print("=" * 70)

# Test imports
print("\n1. Testing imports...")
try:
    from datetime import datetime
    import pandas as pd
    import numpy as np
    from dataclasses import dataclass
    from typing import List, Dict, Tuple, Optional
    print("   ✓ Core modules imported")
except Exception as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test TechnicalAnalyzer.calculate_atr exists
print("\n2. Checking TechnicalAnalyzer.calculate_atr...")
try:
    # Create sample DataFrame
    df = pd.DataFrame({
        'High': [100, 102, 101, 103, 105, 104, 106],
        'Low': [98, 99, 99, 100, 102, 101, 103],
        'Close': [99, 101, 100, 102, 104, 103, 105],
        'Open': [98, 100, 101, 100, 103, 104, 104],
        'Volume': [1000000] * 7
    })
    
    # Import and test
    from Trading import TechnicalAnalyzer
    atr = TechnicalAnalyzer.calculate_atr(df, 14)
    print(f"   ✓ calculate_atr works: ATR = {atr:.2f}")
except Exception as e:
    print(f"   ✗ calculate_atr error: {e}")
    import traceback
    traceback.print_exc()

# Test Strategy classes exist
print("\n3. Checking Strategy classes...")
try:
    from Trading import (
        MomentumStrategy,
        MeanReversionStrategy, 
        PairsStrategy,
        MultiFactorStrategy
    )
    print("   ✓ MomentumStrategy imported")
    print("   ✓ MeanReversionStrategy imported")
    print("   ✓ PairsStrategy imported")
    print("   ✓ MultiFactorStrategy imported")
except Exception as e:
    print(f"   ✗ Strategy import error: {e}")
    import traceback
    traceback.print_exc()

# Test strategy instantiation
print("\n4. Testing strategy instantiation...")
try:
    momentum = MomentumStrategy(lookback_days=126, top_pct=0.25)
    print(f"   ✓ MomentumStrategy created: {momentum.name}")
    
    mean_rev = MeanReversionStrategy(z_threshold=2.0)
    print(f"   ✓ MeanReversionStrategy created: {mean_rev.name}")
    
    pairs = PairsStrategy(z_threshold=2.0)
    print(f"   ✓ PairsStrategy created: {pairs.name}")
    
    multi = MultiFactorStrategy(top_pct=0.20)
    print(f"   ✓ MultiFactorStrategy created: {multi.name}")
except Exception as e:
    print(f"   ✗ Instantiation error: {e}")
    import traceback
    traceback.print_exc()

# Test StatisticalArbitrage.find_pairs signature
print("\n5. Checking StatisticalArbitrage.find_pairs signature...")
try:
    from Trading import StatisticalArbitrage
    import inspect
    
    sig = inspect.signature(StatisticalArbitrage.find_pairs)
    params = list(sig.parameters.keys())
    
    print(f"   Parameters: {params}")
    
    if 'significance_level' in params:
        print("   ⚠ Warning: significance_level still in signature (should be internal)")
    else:
        print("   ✓ Signature correct (no significance_level parameter)")
        
except Exception as e:
    print(f"   ✗ Signature check error: {e}")

# Test DataManager
print("\n6. Checking DataManager...")
try:
    from Trading import DataManager
    print("   ✓ DataManager imported")
    
    # Test if fetch_data method exists
    if hasattr(DataManager, 'fetch_data'):
        print("   ✓ fetch_data method exists")
    else:
        print("   ✗ fetch_data method missing")
        
except Exception as e:
    print(f"   ✗ DataManager error: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
The following should now work without errors:

1. Menu → 23 (Run Quantitative Strategies)
2. Select strategy:
   - 1: Momentum Strategy
   - 2: Mean Reversion Strategy  
   - 3: Pairs Trading Strategy
   - 5: Multi-Factor Strategy
   - 6: Run All & Compare

3. Select universe:
   - 1: S&P 500 Top 50
   - 2: Tech Giants
   - 3: Custom tickers

Expected behavior:
- Strategies generate signals
- No "calculate_atr" errors
- No "find_pairs signature" errors
- Signals displayed in table format
- Option to export to CSV

Note: ML strategy (4) requires trained models via Menu → 10 first.
""")
print("=" * 70)
