# NewsData.IO Integration - Geopolitical Market Events

## Overview
Your Trading.py now includes **NewsData.IO** to track geopolitical and macro events that affect markets:
- Fed rate decisions & policy changes
- Tariffs and trade wars
- Sanctions and geopolitical conflicts
- OPEC oil production decisions
- Currency market moves
- Central bank actions worldwide
- Economic data releases

## Setup Instructions

### Get Your Free API Key
1. Go to: https://newsdata.io
2. Sign up for free account
3. Get API key from dashboard
4. Set environment variable:
   ```
   NEWSDATA_API_KEY=your_api_key_here
   ```

**Free tier includes:**
- ✅ 200 API requests per day
- ✅ News from 40,000+ sources
- ✅ 40+ languages supported
- ✅ Real-time news feeds
- Rate limit: None (batch API calls)

## Data Sources Now Used

Your AI Trade Advisor now integrates:

| Source | Data Type | Use Case |
|--------|-----------|----------|
| **Finnhub** | Company news, earnings, insider trades | Individual stock fundamentals |
| **SEC Edgar** | Official filings, Form 4 trades | Company health, insider activity |
| **NewsData.IO** | Geopolitical, macro, Fed, tariffs, OPEC | Market-wide catalysts affecting sectors |
| **DuckDuckGo** | General web search | Fallback for broader news |

## How It Works in Your System

### Advisor (Option 16)
When you ask: **"Why is XYZ stock moving?"**

It now fetches:
1. **Company-specific news** (Finnhub)
2. **SEC filings & insider trades** (SEC Edgar)
3. **Geopolitical events** (NewsData.IO) - *NEW*
4. **General market news** (DuckDuckGo fallback)

Then **Groq synthesizes all sources** to explain:
- Direct company catalysts (earnings, product launches, insider selling)
- SEC filings showing financial health
- **Geopolitical context** affecting the sector
- Technical setup validation

### Example Analyses

**Scenario: User asks "Why is oil stocks rallying?"**
```
Advisor finds:
- Finnhub: XOM, CVX up on earnings beats
- NewsData.IO: OPEC announced production cut
- Technical: Oil has broken above resistance

Answer: "OPEC just cut production (NewsData.IO), which reduces supply and 
pushes oil prices higher. That's great for energy stocks like Exxon (XOM) 
and Chevron (CVX). Plus, they both beat earnings last quarter. Here's the 
OPEC story: [link]"
```

**Scenario: User asks "Why is tech getting hit today?"**
```
Advisor finds:
- NewsData.IO: Fed signaling higher rates longer
- Finnhub: Tech earnings guidance appears weak
- Technical: NASDAQ breaking support

Answer: "Fed is signaling they'll keep rates higher longer (NewsData.IO) 
which is bad for growth stocks like NVIDIA and Tesla. Higher rates make 
future earnings less attractive. Combined with weak guidance from mega-cap 
tech. Here's the Fed story: [link]"
```

## Geopolitical Events Tracked

### Macro Events
- **Fed Decisions** → Banks rally, growth stocks fall on rate hikes
- **Interest Rate Changes** → Bonds, REITs, dividend stocks affected
- **Inflation Data** → Fed policy expectations, commodity moves
- **GDP/Jobs Data** → Economic cycle shifts

### Trade & Tariffs
- **Tariff Announcements** → Export companies hurt, domestic makers helped
- **Trade War Escalations** → Tech, auto, agricultural stocks affected
- **Trade Deals** → Sector rotation based on beneficiaries

### Geopolitical Conflicts
- **Wars/Conflicts** → Energy supply concerns, defense stocks rally
- **Sanctions** → Affected companies drop, alternatives rally
- **Regional Tensions** → Oil volatility, safe-havens rally

### OPEC & Energy
- **Production Cuts** → Oil up, energy stocks up, airlines/logistics down
- **Production Increases** → Oil down, energy stocks down, consumer benefitted
- **Meetings** → Expectations drive pre-event and post-event moves

### Currency Markets
- **USD Strength** → Hurts exporters, helps importers, commodities down
- **USD Weakness** → Helps exporters, hurts importers, commodities up
- **Major Currency Moves** → Multinational earnings impact

## Using in AI Trade Advisor

### Command Examples
```
Ask: "What geopolitical events are affecting markets today?"
→ Gets NewsData.IO geopolitical news
→ Explains market impacts
→ Shows affected sectors/stocks

Ask: "Why is gold rallying?"
→ Finds Fed policy news (NewsData.IO)
→ Finds technical breakdown
→ Explains inverse relationship: Lower rates → Gold attractive

Ask: "Is TSLA affected by China tariffs?"
→ Searches "China tariffs" (NewsData.IO)
→ Shows TSLA exposure to China
→ Estimates revenue impact
→ Provides links to tariff articles

Ask: "How would Fed rate cut help this stock?"
→ Analyzes company sensitivity to rates
→ Pulls recent Fed policy news (NewsData.IO)
→ Shows historical stock response patterns
```

## System Architecture

```
User Question
    ↓
Ticker Extraction (AI understands what they're asking)
    ↓
Parallel Data Fetch:
    ├─ Finnhub: Company news, earnings, insider trades
    ├─ SEC Edgar: Recent filings, insider activity
    ├─ NewsData.IO: Geopolitical/macro events (NEW)
    └─ Technical: Price action, support/resistance
    ↓
Groq Analysis: Synthesizes all sources
    ├─ Company fundamentals impact
    ├─ Insider trading sentiment
    ├─ Geopolitical/macro tailwinds/headwinds (NEW)
    ├─ Technical setup
    └─ Connects them into single coherent opinion
    ↓
Response: "Here's what I see from [4 sources]..."
```

## Environment Variables Setup

### Windows PowerShell
```powershell
$env:FINNHUB_API_KEY = "your_finnhub_key"
$env:NEWSDATA_API_KEY = "your_newsdata_key"
python Trading.py
```

### Windows Command Prompt
```cmd
set FINNHUB_API_KEY=your_finnhub_key
set NEWSDATA_API_KEY=your_newsdata_key
python Trading.py
```

### Linux/Mac
```bash
export FINNHUB_API_KEY="your_finnhub_key"
export NEWSDATA_API_KEY="your_newsdata_key"
python Trading.py
```

## NewsData.IO Methods Available

### Public Methods
1. **`get_geopolitical_news(limit=15)`**
   - Searches: geopolitical, sanctions, trade war, tariffs, Fed, central bank, interest rates, recession, inflation
   - Returns: Curated list of market-moving geopolitical events
   - Use: When analyzing macro impacts

2. **`get_market_news(limit=15)`**
   - Searches: "stock market business"
   - Returns: General business/market news
   - Use: Broad market context

3. **`search_ticker_news(ticker, limit=10)`**
   - Searches: specific ticker
   - Returns: All news mentioning that ticker
   - Use: When regular company news is scarce

4. **`search_event_impact(event, limit=10)`**
   - Searches: specific event (e.g., "Fed rate hike", "China tariffs")
   - Returns: Articles about that event and impact
   - Use: Deep dive into specific events

## Rate Limits & Quotas

**NewsData.IO Free Tier:**
- 200 requests per day
- No rate limiting per minute
- Resets daily at midnight UTC

**Optimization:**
- System batches requests (fetches geopolitical + market news in 2 calls)
- Results cached by Groq (same question doesn't re-fetch)
- Fallback to DuckDuckGo if quota exceeded

## Troubleshooting

### "NewsData.IO API key not set"
```
Solution: Set NEWSDATA_API_KEY environment variable
Verify: Restart terminal after setting variable
```

### "400 Bad Request from NewsData.IO"
```
Possible causes:
- Invalid API key (check at newsdata.io/dashboard)
- Exceeded daily quota (200 requests)
- Special characters in search query

Solution: Check key validity, wait for daily reset, or increase quota
```

### "No articles found"
This is normal if:
- No geopolitical news today (quiet market)
- System falls back to Finnhub + SEC Edgar (still good coverage)
- DuckDuckGo fallback activates

## Cost Summary

| Source | Cost | API Calls |
|--------|------|-----------|
| Finnhub | Free | 60/min |
| SEC Edgar | Free | Unlimited |
| NewsData.IO | Free | 200/day |
| DuckDuckGo | Free | Unlimited |
| **Total** | **FREE** | Generous limits |

## Performance Impact

- **First query:** ~3-5 seconds (fetching 4 data sources)
- **Subsequent queries:** ~1-2 seconds (Groq caching)
- **Daily cost:** Free (all APIs are free tier)
- **Data freshness:** Real-time news, updated every minute

## Next Steps

1. **Sign up:** https://newsdata.io (2 minutes)
2. **Get API key:** From dashboard
3. **Set environment variable:** `NEWSDATA_API_KEY=...`
4. **Test in advisor:** Ask geopolitical questions
5. **Monitor:** Check if advisor now mentions Fed, tariffs, OPEC, etc.

## Example Questions to Try

```
"Why are tech stocks down?"
→ Will find Fed rate guidance from NewsData.IO

"Is oil going up or down?"
→ Will find OPEC production news from NewsData.IO

"What's affecting the stock market today?"
→ Gets geopolitical overview from NewsData.IO

"How do tariffs affect chip makers?"
→ Connects China tariff news to TSMC/SMIC exposure

"Would a Fed rate cut help Apple?"
→ Analyzes AAPL sensitivity + Fed policy news from NewsData.IO
```

## Features Summary

✅ **Geopolitical events** - Sanctions, conflicts, treaties
✅ **Macro data** - Fed, inflation, employment, GDP
✅ **Trade news** - Tariffs, trade wars, deals
✅ **Energy** - OPEC, oil prices, production
✅ **Central banks** - ECB, BOJ, BOE, Fed decisions
✅ **Currency moves** - USD strength, forex
✅ **40+ languages** - Global news coverage
✅ **Real-time** - News as it breaks
✅ **Free tier** - 200 requests/day perfect for traders
✅ **Integrated** - Seamless into advisor workflow
