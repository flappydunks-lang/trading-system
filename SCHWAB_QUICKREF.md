# Schwab Futures Quick Reference

## Installation
```powershell
pip install schwab-py
```

## Setup (One-Time)
1. Get API credentials: https://developer.schwab.com
2. Run: `python Trading.py` → Option 18
3. Enter App Key & Secret
4. Complete browser authentication

## Workflow

**Integrated with Analysis (Option 1)**

1. Select Option 1 (Analyze Stock/Crypto)
2. Enter futures symbol (e.g., /ES, ES, or ES=F)
3. Select "3. Futures" as instrument type
4. Complete analysis
5. Futures trading menu appears automatically

### Futures Trading Menu Options

After analyzing a futures contract:

| Option | Function | Description |
|--------|----------|-------------|
| 1 | Dashboard | View positions, P&L, account balance |
| 2 | Place Order | Execute trade for analyzed contract |
| 3 | Positions | View all open futures positions |
| 4 | Settings | Configure Schwab credentials |
| 5 | Back | Return to main menu |

## Popular Futures Symbols

### Equity Indexes
- `/ES` - S&P 500 E-mini
- `/NQ` - Nasdaq 100 E-mini
- `/YM` - Dow Jones E-mini
- `/RTY` - Russell 2000 E-mini

### Commodities
- `/CL` - Crude Oil
- `/GC` - Gold
- `/SI` - Silver
- `/NG` - Natural Gas

### Treasuries
- `/ZB` - 30-Year Bond
- `/ZN` - 10-Year Note

## Quick Trade Flow

```
Option 1 → Enter "/ES" → Select "3. Futures" → 
View Analysis → Futures Menu → 
Select "2. Place Order" → BUY/SELL → Confirm
```

## Example Session

```
1. Analyze /ES:
   Main Menu → 1 → "/ES" → Futures → Analysis

2. AI says BUY with 85% confidence

3. Futures menu appears:
   Select 2 (Place Order)

4. Pre-filled with AI recommendation:
   - Side: BUY (from AI)
   - Stop: $5,450 (from AI)
   - Target: $5,520 (from AI)

5. Confirm and execute
```

## Contract Sizes

| Symbol | Size | Value of 1 Point |
|--------|------|------------------|
| /ES | $50 × Index | $50 |
| /NQ | $20 × Index | $20 |
| /YM | $5 × Index | $5 |
| /CL | 1,000 barrels | $1,000 |
| /GC | 100 oz | $100 |

## Risk Warnings

⚠️ High leverage - manage position size
⚠️ Maintain adequate margin
⚠️ Set stop losses
⚠️ Futures can gap overnight

## Troubleshooting

**Not authenticated?** → Run Option 18
**Order rejected?** → Check margin/symbol
**Credentials error?** → Verify in .env file

## Files
- Config: `config/config.json`
- Tokens: `config/schwab_tokens.json`
- Logs: `logs/finalai_YYYYMMDD.log`
