# Charles Schwab Futures Trading Integration Guide

## Overview
FinalAI Quantum v7.0 now supports **direct futures trading** through Charles Schwab's API. Trade E-mini futures, commodities, and more directly from your terminal.

## Supported Futures Contracts

### Equity Index Futures
- **`/ES`** - E-mini S&P 500
- **`/NQ`** - E-mini Nasdaq 100
- **`/YM`** - E-mini Dow Jones
- **`/RTY`** - E-mini Russell 2000

### Commodity Futures
- **`/CL`** - Crude Oil
- **`/GC`** - Gold
- **`/SI`** - Silver
- **`/NG`** - Natural Gas

### Treasury Futures
- **`/ZB`** - 30-Year T-Bond
- **`/ZN`** - 10-Year T-Note
- **`/ZF`** - 5-Year T-Note

## Setup Instructions

### Step 1: Install Required Library

```powershell
pip install schwab-py
```

### Step 2: Get Schwab API Credentials

1. **Go to Schwab Developer Portal**
   - Visit: https://developer.schwab.com
   - Sign in with your Charles Schwab account

2. **Register Your Application**
   - Navigate to: My Apps → Register an App
   - Fill out the form:
     - **App Name**: `FinalAI Trading` (or any name you prefer)
     - **Callback URL**: `https://localhost:8182`
     - **Permissions**: Check both:
       - ✓ Accounts and Trading Production
       - ✓ Market Data Production
   
3. **Save Your Credentials**
   - Copy your **App Key**
   - Copy your **App Secret** (keep this secure!)

### Step 3: Enable Futures Trading on Your Account

1. Log into schwab.com
2. Navigate to: **Trade → Futures & Forex**
3. Complete the futures trading application
4. Wait for approval (typically 1-2 business days)

### Step 4: Configure FinalAI

Run the application and select option **18 (Preflight Setup)**:

```powershell
python Trading.py
```

During setup:
1. Answer "yes" when asked about Schwab futures
2. Enter your App Key
3. Enter your App Secret
4. Complete browser authentication when prompted

## Features

### 1. Futures Dashboard (Option 22)
View real-time:
- Account balance and buying power
- Current positions with P&L
- Live market quotes for popular futures
- Available margin

### 2. Place Futures Orders (Option 23)
Execute trades with:
- **Market Orders**: Immediate execution at current price
- **Limit Orders**: Execute at your specified price or better
- **Long/Short**: Open positions in either direction
- **Multiple Contracts**: Trade 1 or more contracts per order

## Usage Examples

### Example 1: Buy E-mini S&P 500

1. Select **Option 23** (Place Futures Order)
2. Choose **1** (/ES - E-mini S&P 500)
3. Select **1** (BUY)
4. Enter quantity: **1** contract
5. Choose **1** (MARKET order)
6. Confirm the order

### Example 2: Short Crude Oil with Limit

1. Select **Option 23**
2. Choose **5** (/CL - Crude Oil)
3. Select **2** (SELL)
4. Enter quantity: **2** contracts
5. Choose **2** (LIMIT order)
6. Enter limit price: **$75.50**
7. Confirm the order

### Example 3: Monitor Positions

1. Select **Option 22** (Schwab Futures Dashboard)
2. View:
   - Current positions
   - Real-time P&L
   - Account margin status
3. Press **1** to refresh
4. Press **2** to place a new order

## Risk Management

### Futures Contract Specifications

| Symbol | Contract Size | Tick Size | Approx. Margin* |
|--------|---------------|-----------|-----------------|
| /ES    | $50 × Index   | $12.50    | $12,000         |
| /NQ    | $20 × Index   | $5.00     | $16,000         |
| /YM    | $5 × Index    | $5.00     | $7,500          |
| /CL    | 1,000 barrels | $10.00    | $6,000          |
| /GC    | 100 oz        | $10.00    | $8,500          |

*Margins vary by broker and market conditions

### Important Considerations

⚠️ **Leverage Risk**
- Futures use high leverage
- Small price movements = large P&L swings
- Never risk more than 1-2% of account per trade

⚠️ **Margin Calls**
- Maintain sufficient margin at all times
- Positions may be liquidated if margin falls below requirements

⚠️ **Market Hours**
- E-mini futures trade nearly 24 hours
- Be aware of rollover dates (quarterly)

## API Rate Limits

Schwab API limits:
- **120 requests per minute** for market data
- **60 requests per minute** for trading

FinalAI automatically manages rate limits.

## Troubleshooting

### "Not authenticated" Error
- Run **Option 18** to complete authentication
- Check your App Key and Secret are correct
- Ensure token file exists: `config/schwab_tokens.json`

### "Futures trading not enabled" Error
- Verify futures are approved on your Schwab account
- Contact Schwab support if application is pending

### Order Rejected
- **Insufficient Margin**: Deposit more funds
- **Invalid Symbol**: Check futures symbol format (must start with `/`)
- **Market Closed**: Some futures have limited trading hours

### Authentication Browser Not Opening
- Check firewall settings
- Manually visit the callback URL when prompted
- Copy the full redirect URL back into the terminal

## Security Best Practices

✅ **DO:**
- Keep your App Secret secure
- Use environment variables for credentials
- Enable two-factor authentication on Schwab account
- Review order confirmations carefully

❌ **DON'T:**
- Share your API credentials
- Commit credentials to version control
- Trade without understanding contract specifications
- Over-leverage your account

## Advanced Features

### 1. Integration with Analysis
FinalAI can analyze futures just like stocks:
```
Option 1 → Enter "/ES" → Get full technical analysis
```

### 2. Multi-Timeframe Analysis
```
Option 9 → Enter "/NQ" → See analysis across multiple timeframes
```

### 3. News & Market Intel
```
Option 3 → Track news affecting commodity futures
```

## Support & Resources

### Schwab Resources
- Developer Portal: https://developer.schwab.com
- API Documentation: https://developer.schwab.com/products/trader-api--individual
- Support: https://developer.schwab.com/support

### schwab-py Library
- GitHub: https://github.com/alexgolec/schwab-py
- Documentation: https://schwab-py.readthedocs.io

### FinalAI Support
- Check logs: `logs/finalai_YYYYMMDD.log`
- Configuration: `config/config.json`
- Token storage: `config/schwab_tokens.json`

## Example Trading Workflow

```
┌─────────────────────────────────────────┐
│ 1. Run FinalAI                          │
│    python Trading.py                    │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 2. View Dashboard (Option 22)           │
│    - Check account balance              │
│    - Review positions                   │
│    - Monitor market quotes              │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 3. Analyze Market (Option 1)            │
│    - Enter /ES, /NQ, /CL, etc.          │
│    - Get AI predictions                 │
│    - Check technical indicators         │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 4. Place Order (Option 23)              │
│    - Select contract                    │
│    - Choose BUY/SELL                    │
│    - Set quantity & price               │
│    - Confirm execution                  │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 5. Monitor Position (Option 22)         │
│    - Track real-time P&L                │
│    - Adjust if needed                   │
│    - Close when target reached          │
└─────────────────────────────────────────┘
```

## Disclaimer

⚠️ **IMPORTANT DISCLAIMER**

Futures trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. 

- This software is for informational purposes only
- Not financial advice
- Trade at your own risk
- Consult a licensed financial advisor

The developers of FinalAI Quantum are not responsible for any trading losses incurred through use of this software.

---

**Ready to trade futures?** Run `python Trading.py` and select **Option 18** to get started! 🚀
