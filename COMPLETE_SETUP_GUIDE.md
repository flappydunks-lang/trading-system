# Complete Trading Bot & AI Advisor Setup Guide

## Quick Start (5 minutes)

Your Trading.py now has **4 integrated news/data sources** that work together:

### 1. Finnhub (Required for best results)
- **Sign up:** https://finnhub.io
- **Get key:** https://finnhub.io/dashboard/api-keys
- **Set env var:** `FINNHUB_API_KEY=your_key`
- **What it gives:** Company news, earnings, insider trades, analyst ratings

### 2. SEC Edgar (Automatic - No setup!)
- **Cost:** Free, no API key needed
- **What it gives:** SEC filings (10-K, 10-Q, 8-K), official insider trades

### 3. NewsData.IO (NEW - For geopolitical events)
- **Sign up:** https://newsdata.io
- **Get key:** From dashboard after signup
- **Set env var:** `NEWSDATA_API_KEY=your_key`
- **What it gives:** Fed decisions, tariffs, geopolitical events, OPEC news

### 4. DuckDuckGo (Automatic - Fallback)
- **Cost:** Free
- **What it gives:** General web search results

## Complete Setup Steps

### Step 1: Install Requirements
```bash
pip install finnhub-python requests beautifulsoup4
```

### Step 2: Get API Keys (2 minutes each)

**Finnhub:**
1. Go to https://finnhub.io
2. Sign up (free email)
3. Dashboard → API keys
4. Copy your key

**NewsData.IO:**
1. Go to https://newsdata.io
2. Sign up (free email)
3. Dashboard → get key
4. Copy your key

### Step 3: Set Environment Variables

**Windows PowerShell:**
```powershell
$env:FINNHUB_API_KEY = "your_finnhub_key"
$env:NEWSDATA_API_KEY = "your_newsdata_key"
python Trading.py
```

**Windows Command Prompt:**
```cmd
set FINNHUB_API_KEY=your_finnhub_key
set NEWSDATA_API_KEY=your_newsdata_key
python Trading.py
```

**Linux/Mac:**
```bash
export FINNHUB_API_KEY="your_finnhub_key"
export NEWSDATA_API_KEY="your_newsdata_key"
python Trading.py
```

### Step 4: Verify Setup
```
Run Trading.py → Select "16. 💬 AI Trade Advisor"
Ask: "Why is Apple stock up?"
→ Should see sources loading:
   ✓ Finnhub: X company news articles
   ✓ SEC Edgar: X recent filings
   ✓ Insider Trades: X recent trades
   ✓ NewsData.IO: X geopolitical/macro events
   ✓ Web search: X additional articles
→ Should see comprehensive analysis with links
```

## What You Get

### AI Trade Advisor Features

**1. Company-Level Analysis**
- Real-time company news (Finnhub)
- Recent SEC filings (10-K, 10-Q, 8-K)
- Insider trading activity
- Analyst consensus ratings
- Earnings dates & estimates

**2. Geopolitical Impact** ⭐ NEW
- Fed rate decisions and guidance
- Tariff announcements and trade wars
- Sanctions and geopolitical conflicts
- OPEC oil production decisions
- Currency movements
- Central bank policy changes

**3. Technical Analysis**
- Support/resistance levels
- Trend identification
- RSI and momentum
- Price patterns

**4. Comprehensive Synthesis**
- Groq AI combines all sources
- Explains cause-effect chains
- Provides direct article links
- Gives actionable insights

## Example Conversations

### Example 1: Company Question
```
You: "Why is Tesla up today?"

Advisor fetches:
- Finnhub: Latest TSLA news and insider activity
- SEC Edgar: Recent 8-K filings
- NewsData.IO: Any tariff/geopolitical news affecting EV industry
- Technical: Price action analysis

Response: "Tesla jumped on rumors of new factory announcement (Source: 
Bloomberg via Finnhub). Plus, recent CEO insider purchases suggest confidence 
(SEC data). Geopolitically, new China EV subsidies are also helping the 
sector (NewsData.IO). Technically, broke above $200 resistance. Here's the 
factory story: [link]"
```

### Example 2: Macro Event Question
```
You: "How would a Fed rate cut affect my portfolio?"

Advisor:
- Gets latest Fed policy news (NewsData.IO)
- Analyzes each stock's rate sensitivity
- Shows historical patterns
- Provides actionable guidance

Response: "Fed rate cut would be huge for tech stocks (lower discount rates 
on future earnings) and REITs (more competitive yields). Gold would rally 
(lower opportunity cost). But banks might suffer (lower lending margins). 
Here's the latest Fed guidance: [link]"
```

### Example 3: Geopolitical Question
```
You: "How do China tariffs affect chip stocks?"

Advisor:
- Searches for China tariff news (NewsData.IO)
- Analyzes TSMC, SMIC, QCOM exposure
- Shows supply chain impacts
- Connects to stock movements

Response: "New China tariffs hurt semiconductor shipments to China. That's 
bad for TSMC (40% China revenue) and companies like Qualcomm that depend on 
China sales. Good for US chip makers like Intel who'll capture domestic 
demand. Here's the tariff details: [link]"
```

## API Limits & Costs

| Service | Free Tier | Limit | Cost |
|---------|-----------|-------|------|
| **Finnhub** | ✅ Yes | 60 API calls/min | Free |
| **SEC Edgar** | ✅ Yes | Unlimited | Free |
| **NewsData.IO** | ✅ Yes | 200 requests/day | Free |
| **DuckDuckGo** | ✅ Yes | Unlimited | Free |
| **Groq (AI)** | ✅ Yes | 60 API calls/min | Free |
| **Total** | **FREE** | Generous | **$0/month** |

## Data Flow Diagram

```
User asks: "Why is XYZ stock moving?"
    │
    ├─→ Finnhub (Company news, earnings, insider trades)
    │
    ├─→ SEC Edgar (Official filings, Form 4 trades)
    │
    ├─→ NewsData.IO (Geopolitical, Fed, tariffs, OPEC)
    │
    ├─→ Technical Analysis (Price action)
    │
    └─→ DuckDuckGo (Web search fallback)
    
    All sources feed into Groq AI which:
    - Synthesizes all information
    - Identifies cause-effect relationships
    - Finds relevant articles/links
    - Explains market dynamics
    - Provides actionable insights
    
    Returns: Comprehensive analysis with sources
```

## Trading Bot Integration

The trading bot also uses these sources for:
- **Entry signals:** Technical + news confirmation
- **Risk assessment:** Geopolitical events affecting sector
- **Position sizing:** Insider activity and filing changes
- **Exit triggers:** Major news/geopolitical events

## Pro Tips

### 1. Maximize Data Quality
- Set both API keys (Finnhub + NewsData.IO)
- If quota exceeded, system falls back gracefully
- SEC Edgar has no quota (use liberally)

### 2. Ask Specific Questions
```
✅ Good: "Why is oil jumping today?"
   ❌ Bad: "How are stocks?"

✅ Good: "How would Fed rate hike affect tech?"
   ❌ Bad: "Fed decision?"

✅ Good: "What geopolitical events could hurt semiconductor stocks?"
   ❌ Bad: "Geopolitical news?"
```

### 3. Verify Information
- Advisor always provides source links
- Click links to verify claims
- Check multiple sources for consensus
- Be skeptical of single-source opinions

### 4. Watch Geopolitical Calendar
- Fed announcements (NewsData.IO alerts you)
- OPEC meetings (oil impact)
- Major elections/political events
- Trade negotiations/tariff announcements
- Geopolitical conflicts

## Troubleshooting

### Problem: "No data found"
**Solutions:**
1. Check API keys are set correctly
2. Verify internet connection
3. Try a major ticker (AAPL, MSFT, TSLA)
4. Check API dashboard for quota exceeded
5. Fallback uses DuckDuckGo (always works)

### Problem: "API key not found"
**Windows:**
- Close and reopen terminal after setting env vars
- Use `echo %FINNHUB_API_KEY%` to verify it's set

**Linux/Mac:**
- Use `echo $FINNHUB_API_KEY` to verify it's set

### Problem: Slow responses
**Solutions:**
1. First query fetches from 4 sources (normal, ~3-5s)
2. Subsequent queries use Groq caching (faster)
3. If very slow, one API might be down (fallback works)
4. Check your internet connection

## Checking Your Setup

```python
# Run this to verify all APIs work
from Trading import FinnhubAnalyzer, SECEdgarAnalyzer, NewsDataAnalyzer

# Test Finnhub
finnhub_news = FinnhubAnalyzer.get_news("AAPL", limit=1)
print(f"Finnhub: {len(finnhub_news)} articles") # Should be ≥1

# Test SEC Edgar
sec_filings = SECEdgarAnalyzer.get_recent_filings("AAPL", limit=1)
print(f"SEC Edgar: {len(sec_filings)} filings") # Should be ≥1

# Test NewsData.IO
newsdata_geo = NewsDataAnalyzer.get_geopolitical_news(limit=1)
print(f"NewsData.IO: {len(newsdata_geo)} events") # Should be ≥1
```

## Next Steps

1. **Get both API keys** (Finnhub + NewsData.IO) - 5 minutes
2. **Set environment variables** - 1 minute
3. **Test in advisor** - Ask a geopolitical question
4. **Monitor market moves** - Use advisor to track Fed, tariffs, etc.
5. **Integrate into trading** - Use advisor signals for trades

## Questions?

**For Finnhub issues:** Check https://finnhub.io/docs/api
**For NewsData.IO issues:** Check https://newsdata.io/docs
**For SEC Edgar issues:** Check https://www.sec.gov/cgi-bin
**For Trading.py issues:** Check log file in /logs directory

## Files Reference

- **FINNHUB_SEC_SETUP.md** - Details on Finnhub + SEC Edgar
- **NEWSDATA_SETUP.md** - Details on NewsData.IO geopolitical events
- **Trading.py** - Main application with all integrations

## Summary

You now have a **professional-grade AI trading advisor** that:
- ✅ Tracks company fundamentals (Finnhub)
- ✅ Monitors insider activity (SEC)
- ✅ Watches geopolitical events (NewsData.IO)
- ✅ Analyzes technical setups
- ✅ Synthesizes all sources with AI
- ✅ Provides actionable insights with source links
- ✅ Completely FREE to use

**Total setup time:** ~10 minutes
**Total monthly cost:** $0
**Data freshness:** Real-time
**Accuracy:** Cites all sources, verified links
