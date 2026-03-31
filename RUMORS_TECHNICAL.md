# Rumors Tracking Implementation - Technical Summary

## Architecture

### Data Flow: News Request → Multiple Sources → Groq Analysis

```
User Question: "What's the news on AAPL?"
    ↓
fetch_news_for_ticker(ticker='AAPL')
    ↓
    ├─→ [1] FinnhubAnalyzer.get_news() → 15-20 verified articles
    ├─→ [2] SECEdgarAnalyzer.get_recent_filings() → 3-5 official filings
    ├─→ [3] FinnhubAnalyzer.get_insider_trades() → 2-5 insider transactions
    ├─→ [4] NewsDataAnalyzer.get_geopolitical_news() → 10-15 market-moving events
    └─→ [5] NewsDataAnalyzer.get_rumors_and_speculation() → 8 unverified rumors
            (NEW FEATURE - searches for speculation keywords)
    ↓
    Build article list:
    - Verified articles get standard format
    - Rumors get marked with ⚠️, "RUMOR:", [UNVERIFIED]
    - Set verified=False, confidence='UNVERIFIED' for rumors
    ↓
generate_comprehensive_analysis(ticker, articles_with_rumors)
    ↓
    Split articles:
    - verified_count = articles where verified != False
    - rumor_count = articles where verified == False OR 'RUMOR' in title
    ↓
    Create Groq prompt with:
    - VERIFIED articles section (numbered)
    - UNVERIFIED rumors section (marked with ⚠️)
    - Separate instructions for each
    ↓
    Groq creates analysis with sections:
    1. Verified synthesis (from facts only)
    2. Rumor tracker (plausibility ratings)
    3. Impact assessment (could rumors affect price?)
    4. Bottom line (thesis based on verified, noting rumors)
    ↓
Return comprehensive analysis to user
    ↓
User sees: Green checkmarks (verified) + Yellow warnings (rumors)
```

## Code Changes Summary

### 1. New Method in NewsDataAnalyzer Class

**Location:** Lines 3771-3816 in Trading.py

```python
@staticmethod
def get_rumors_and_speculation(ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch unverified rumors, speculation, and social media commentary"""
    
    # Searches keywords: rumor, speculation, unconfirmed, alleged, reported, claims
    # Returns articles with:
    #   - type='RUMOR'
    #   - verified=False
    #   - confidence='UNVERIFIED'
```

### 2. Updated fetch_news_for_ticker() Function

**Location:** Lines 8611-8624 in Trading.py

```python
# QUINTERNARY: Rumors & Unverified Speculation
try:
    rumors = NewsDataAnalyzer.get_rumors_and_speculation(ticker, limit=8)
    if rumors:
        for rumor in rumors:
            articles.append({
                'title': f"⚠️ RUMOR: {rumor.get('title', '')}",
                'source': f"{rumor.get('source')} [UNVERIFIED]",
                'verified': False,
                'confidence': 'UNVERIFIED',
                ...
            })
```

### 3. Enhanced generate_comprehensive_analysis() Function

**Location:** Lines 8264-8400 in Trading.py

**Key Changes:**
```python
# Separate verified from rumors
verified_count = count articles where verified != False
rumor_count = count articles where verified == False

# Build article list with separation
for article in articles[:num_articles]:
    if verified:
        article_list += f"{verified_count}. {title}"
    else:
        rumor_list += f"⚠️ RUMOR #{rumor_count}: {title}"

# Pass both to Groq prompt with instructions:
# - "Read and understand ALL {verified_count} verified articles"
# - "Also NOTE the {rumor_count} unverified rumors but DO NOT treat as facts"
# - "Cite specific article numbers when discussing VERIFIED news"
# - "When discussing rumors, clearly mark them as 'unverified speculation'"

# New Groq prompt sections:
# - **SYNTHESIS & DOMINANT NARRATIVE** (Based on Verified Sources)
# - **RUMORS & SPECULATION TRACKER** (Plausibility ratings)
# - **THE BOTTOM LINE OPINION** (Could rumors change outlook?)
```

## Testing Checklist

### Manual Testing:

- [ ] Ask advisor: "What's the news on AAPL?"
- [ ] Verify output shows:
  - ✅ Green checkmarks for verified sources
  - ⚠️ Yellow warnings for rumors
  - [UNVERIFIED] tags on rumor sources
- [ ] Check Groq output has:
  - Separate "RUMORS & SPECULATION TRACKER" section
  - Plausibility ratings (HIGH/MEDIUM/LOW)
  - Clear statement that investment thesis based on verified facts only

- [ ] Verify rumors don't appear for:
  - Technical analysis queries (shouldn't need rumors)
  - Price target queries (rumors noted separately)
  - Earnings questions (focus on verified data)

### Code Testing:

- [ ] Syntax check: `mcp_pylance_mcp_s_pylanceSyntaxErrors()` - PASS ✅
- [ ] Import check: All new methods properly indented
- [ ] Error handling: Rumors fetch gracefully handles API failures
- [ ] Data validation: All rumors have required fields

## Configuration

### API Key Required:
- NewsData.IO API key (environment variable: `NEWSDATA_API_KEY`)
- Same key used for both geopolitical news AND rumors

### Tuning Parameters:
```python
# In fetch_news_for_ticker():
rumors = NewsDataAnalyzer.get_rumors_and_speculation(ticker, limit=8)
# Change limit=8 to get more/fewer rumors per search

# In NewsDataAnalyzer.get_rumors_and_speculation():
keywords = ['rumor', 'speculation', 'unconfirmed', 'alleged', 'reported', 'claims']
# Add/remove keywords to broaden/narrow rumor search
```

## User Experience Flow

### Step 1: Ask Question
```
User: "What's happening with Tesla?"
```

### Step 2: See Data Collection
```
🌍 Searching for news on TSLA...
✓ Finnhub: 12 company news articles
✓ SEC Edgar: 2 recent filings
✓ Insider Trades: 1 recent trade
✓ NewsData.IO: 8 geopolitical/macro events
⚠️  Rumors/Speculation: 6 unverified reports found
✓ Total: 29 sources compiled
```

### Step 3: Receive Analysis
```
[🤖 GROQ SYNTHESIS OF 23 VERIFIED + 6 RUMOR SOURCES FOR TSLA]

**SYNTHESIS & DOMINANT NARRATIVE** (Based on Verified Sources):
[Analysis of verified data only]

**RUMORS & SPECULATION TRACKER**:
1. ⚠️ "Tesla planning $10B AI acquisition" - Plausibility: MEDIUM
2. ⚠️ "Musk stepping down as CEO" - Plausibility: LOW
[etc]

**THE BOTTOM LINE OPINION**:
[Investment thesis based on verified facts, noting rumor context]
```

### Step 4: Make Informed Decision
User understands:
- What's fact (verified) vs. speculation (rumor)
- Which rumors are plausible vs. noise
- How rumors might affect price even if false
- Whether to factor rumors into trading decision

## Success Metrics

✅ **Feature is working when:**
1. Rumors appear in output with ⚠️ markers
2. Each rumor has [UNVERIFIED] label
3. Groq analysis includes "RUMORS & SPECULATION TRACKER" section
4. Plausibility ratings shown for each rumor (HIGH/MEDIUM/LOW)
5. Investment thesis clearly separated from rumor speculation
6. Console shows rumor count alongside verified counts

## Known Limitations

1. **NewsData.IO limited by API tier**
   - Free tier: 200 calls/day
   - If queries exhaust limit, rumors won't fetch (graceful failure)

2. **Keyword-based search**
   - Searches for explicit rumor keywords
   - May miss rumors not labeled as such
   - False positives possible (articles containing "rumor" but not rumors)

3. **No rumor tracking over time**
   - Doesn't track if rumors later confirmed
   - Each query starts fresh

4. **No social media integration yet**
   - Only searches NewsData.IO sources
   - Doesn't tap Reddit, Twitter, StockTwits
   - Could be enhanced in future

5. **Groq plausibility assessment**
   - Relies on AI judgment (not verified fact-check)
   - Ratings subjective, not definitive

## Future Enhancements

1. **Multi-source rumors:**
   - Add Reddit API integration (r/investing, r/stocks, r/[ticker])
   - Add Twitter/X API (track mentions of ticker + speculation keywords)
   - Add Stocktwits data (sentiment on rumors)

2. **Rumor persistence:**
   - Track rumors over time
   - Mark when rumors confirmed/debunked
   - Build rumor credibility scores

3. **Advanced filtering:**
   - Allow users to toggle rumors on/off
   - Filter by plausibility level (show only HIGH plausibility)
   - Show source credibility of rumors

4. **Rumor impact analysis:**
   - Correlate historical stock moves to rumor plausibility
   - Track which rumors actually moved price
   - Build "rumor reliability" index

5. **Fact-checking integration:**
   - Connect to FactCheck.org API
   - Cross-reference rumors against fact-check databases
   - Automatic verification when rumors debunked

---

**Implementation Date:** January 2025  
**Status:** ✅ Complete and Integrated  
**Files Modified:** Trading.py (lines 3771-3816, 8264-8400, 8611-8624)  
**Files Created:** RUMORS_FEATURE.md, RUMORS_EXAMPLES.md, RUMORS_TECHNICAL.md
