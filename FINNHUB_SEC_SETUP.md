# Finnhub & SEC Edgar Integration Setup

## Overview
Your Trading.py now has enhanced data sources for the AI Trade Advisor:
- **Finnhub API**: Real-time company news, earnings, analyst ratings, insider trades
- **SEC Edgar**: Official SEC filings (10-K, 10-Q, 8-K) and insider trading data
- **DuckDuckGo**: Web search fallback for general news

## Setup Instructions

### 1. Finnhub (FREE - No credit card required)
1. Go to: https://finnhub.io
2. Sign up for free account
3. Get your API key from: https://finnhub.io/dashboard/api-keys
4. Set environment variable:
   ```
   FINNHUB_API_KEY=your_api_key_here
   ```

**Free tier includes:**
- ✅ Company news (up to 1000/month)
- ✅ Insider trading data
- ✅ Earnings calendar
- ✅ Analyst ratings/recommendations
- ✅ Company profile
- ✅ Crypto data (limited)
- Rate limit: 60 API calls/minute

### 2. SEC Edgar (COMPLETELY FREE)
No API key needed! The SEC provides free access to:
- ✅ All company filings (10-K, 10-Q, 8-K, 4, etc.)
- ✅ Insider trading data (Form 4)
- ✅ Company facts and financial metrics
- ✅ Historical filings database

## How It Works in Your AI Trade Advisor

When you ask about a stock, the system now:

1. **Fetches Finnhub data first** (primary source):
   - Company-specific news articles
   - Insider trading activity
   - Earnings dates and estimates
   - Analyst consensus ratings

2. **Fetches SEC Edgar data** (official source):
   - Recent SEC filings (10-K annual, 10-Q quarterly, 8-K events)
   - Insider trading details (Form 4)
   - Company financial facts

3. **Falls back to web search** (if needed):
   - General market news from DuckDuckGo
   - Additional articles for comprehensive context

4. **AI analysis**:
   - Groq synthesizes all sources
   - Provides comprehensive market opinion
   - Cites specific sources and data

## Example Usage

### Setting Environment Variables

**Windows PowerShell:**
```powershell
$env:FINNHUB_API_KEY = "your_api_key"
python Trading.py
```

**Windows Command Prompt:**
```cmd
set FINNHUB_API_KEY=your_api_key
python Trading.py
```

**Linux/Mac:**
```bash
export FINNHUB_API_KEY="your_api_key"
python Trading.py
```

### In the AI Trade Advisor

Ask natural questions:
```
Ask: "Why is Apple stock up today?"
→ Gets Finnhub news + SEC filings
→ Analyzes insider trades
→ Returns comprehensive analysis with links

Ask: "Show me Tesla's latest earnings"
→ Fetches SEC Edgar 8-K filing
→ Gets Finnhub earnings data
→ Shows analyst ratings

Ask: "Who's selling at Microsoft?"
→ Gets insider trading data from SEC
→ Shows selling patterns
→ Highlights large transactions
```

## Data Sources Used

### Finnhub Coverage
- **News**: Real-time company news from 4000+ sources
- **Insider Trades**: Form 4 filings, insider names, positions, transactions
- **Earnings**: Upcoming dates, EPS estimates, historical results
- **Ratings**: Buy/Hold/Sell recommendations from 500+ analysts
- **Profile**: Company name, industry, market cap, website

### SEC Edgar Coverage
- **Form 10-K**: Annual company reports
- **Form 10-Q**: Quarterly reports
- **Form 8-K**: Major corporate events
- **Form 4**: Insider trades (free real-time data)
- **XBRL Data**: Financial metrics (Assets, Liabilities, Revenue, etc.)

## API Rate Limits

### Finnhub (Free Tier)
- 60 API calls per minute
- No daily limit
- No authentication delay

### SEC Edgar
- Unlimited (no rate limits)
- No API key needed
- Government servers are stable

### DuckDuckGo (Fallback)
- Unlimited searches
- No API key needed

## Troubleshooting

### "Finnhub API key not set"
```
Solution: Set FINNHUB_API_KEY environment variable
Windows: set FINNHUB_API_KEY=your_key
Linux/Mac: export FINNHUB_API_KEY="your_key"
```

### "No articles found"
- Check ticker symbol is correct
- Verify API key is valid at https://finnhub.io/dashboard
- Try a major ticker (AAPL, MSFT, TSLA) first
- DuckDuckGo fallback will activate if APIs fail

### "SEC Edgar CIK lookup failed"
- Some ticker symbols may not be in SEC database
- This is normal for very new or OTC stocks
- Use major tickers for best results

## Performance Tips

1. **First run may be slow** (loading data from multiple sources)
2. **Subsequent queries are faster** (data is cached by Groq)
3. **Turn off unneeded sources** if you want faster responses:
   - Comment out FinnhubAnalyzer calls if you don't need insider data
   - Comment out SECEdgarAnalyzer if you don't need filings

## Feature Summary

| Feature | Source | Free? | Setup Required |
|---------|--------|-------|-----------------|
| Company News | Finnhub | ✅ | API key needed |
| Insider Trades | Finnhub + SEC | ✅ | API key for Finnhub |
| SEC Filings | SEC Edgar | ✅ | None |
| Earnings | Finnhub | ✅ | API key needed |
| Analyst Ratings | Finnhub | ✅ | API key needed |
| Company Profile | Finnhub + SEC | ✅ | API key for Finnhub |
| Web Search | DuckDuckGo | ✅ | None |

## Next Steps

1. Sign up at Finnhub.io (takes 2 minutes)
2. Get your free API key
3. Set FINNHUB_API_KEY environment variable
4. Run Trading.py and use the AI Trade Advisor (option 16)
5. Ask questions about stocks - it'll pull real data!

Example: "Why is AAPL going up?"
→ Gets Finnhub news
→ Checks SEC for insider trades
→ Analyzes with Groq
→ Returns complete analysis
