#!/usr/bin/env python3
"""Quick test to debug AI performance tracking"""

import pandas as pd
from pathlib import Path

tracking_file = Path("results/ai_performance_tracking.csv")

if not tracking_file.exists():
    print("No tracking file found!")
    exit(1)

df = pd.read_csv(tracking_file)
print(f"Total trades: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst row:")
print(df.iloc[0])

open_trades = df[df['status'] == 'OPEN']
print(f"\n\nOpen trades: {len(open_trades)}")

if len(open_trades) > 0:
    for idx, row in open_trades.iterrows():
        print(f"\n--- Trade {idx} ---")
        print(f"Ticker: {row['ticker']}")
        print(f"Action: {row['action']}")
        print(f"Entry: {row['entry_price']}")
        print(f"Stop: {row['stop_loss']}")
        print(f"Risk: {row['risk_amount']}")
        
        # Check if position_size column exists
        if 'position_size' in row:
            print(f"Position size: {row.get('position_size', 'N/A')}")
            if pd.notna(row['position_size']) and row['position_size'] != '':
                shares = float(row['position_size'])
            else:
                price_distance = abs(float(row['entry_price']) - float(row['stop_loss']))
                shares = float(row['risk_amount']) / price_distance if price_distance > 0 else 0
                print(f"Calculated shares: {shares}")
        else:
            print("NO POSITION_SIZE COLUMN!")
            price_distance = abs(float(row['entry_price']) - float(row['stop_loss']))
            shares = float(row['risk_amount']) / price_distance if price_distance > 0 else 0
            print(f"Calculated shares from risk: {shares}")
        
        print(f"Current hypothetical_pnl in CSV: {row.get('hypothetical_pnl', 'N/A')}")
