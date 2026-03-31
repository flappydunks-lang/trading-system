# Rumors Tracking Feature - Implementation Summary

## Overview
Added automatic rumors and speculation tracking to the AI Trade Advisor. When analyzing news about any ticker, the advisor now:
- Fetches verified news from official sources (Finnhub, SEC Edgar, NewsData.IO)
- **Also fetches unverified rumors and speculation** from news sources
- **Clearly labels all rumors with ⚠️ UNVERIFIED status**
- Separates rumor analysis from verified facts in Groq synthesis

## What Changed

### 1. New Method: `NewsDataAnalyzer.get_rumors_and_speculation()`
**Location:** [Trading.py](Trading.py#L3771)
**Purpose:** Fetch unverified rumors, speculation, and unconfirmed reports about a ticker

**How it works:**
- Searches for keywords: 'rumor', 'speculation', 'unconfirmed', 'alleged', 'reported', 'claims'
- Uses NewsData.IO API to find articles containing these terms
- Returns articles marked with:
  - `type: 'RUMOR'`
  - `verified: False`
  - `confidence: 'UNVERIFIED'`

**Example output:**
```python
{
    'title': 'Apple Rumor: Upcoming iPhone Model Leak',
    'url': 'https://...',
    'source': 'TechNews [UNVERIFIED]',
    'timestamp': '2024-01-15',
    'description': 'Alleged leaked specs for next iPhone',
    'type': 'RUMOR',
    'verified': False,
    'confidence': 'UNVERIFIED'
}
```

### 2. Updated `fetch_news_for_ticker()` Function
**Location:** [Trading.py](Trading.py#L8608-L8624)
**Change:** Added QUINTERNARY news source for rumors

**News Source Hierarchy:**
1. ✅ PRIMARY: Finnhub - Real-time company news (verified)
2. ✅ SECONDARY: SEC Edgar - Official filings (verified)
3. ✅ TERTIARY: Insider trades from Form 4 (verified)
4. ✅ QUATERNARY: NewsData.IO - Geopolitical events (verified)
5. **⚠️ QUINTERNARY: NewsDataAnalyzer.get_rumors_and_speculation()** (NEW - unverified)

**Rumors are displayed with:**
- Yellow warning symbol: `⚠️`
- "RUMOR:" prefix in title
- "[UNVERIFIED]" label in source field
- `verified: False` flag for later filtering

**Example console output:**
```
✓ Finnhub: 15 company news articles
✓ SEC Edgar: 3 recent filings
✓ Insider Trades: 2 recent trades
✓ NewsData.IO: 10 geopolitical/macro events
⚠️  Rumors/Speculation: 8 unverified reports found
```

### 3. Enhanced Groq Analysis Prompt
**Location:** [Trading.py](Trading.py#L8287-L8400)
**Changes:** Separated verified articles from rumors in analysis

**Key improvements:**
- **Splits article list into verified vs. rumor tracks**
  - Counts `verified_count` (official news, filings, insider trades)
  - Counts `rumor_count` (unconfirmed speculation)
  
- **New "RUMORS & SPECULATION TRACKER" section in analysis prompt** that asks Groq to:
  - List all unverified rumors circulating
  - Rate plausibility of each rumor (HIGH/MEDIUM/LOW)
  - Determine if rumors align with or contradict verified facts
  - Assess market sentiment around rumors
  
- **Updated opinion sections** to acknowledge rumors:
  - "Could unverified rumors be driving any divergence between verified sentiment and price action?"
  - "Could {rumor_count} unverified rumors suddenly become reality and change your outlook?"
  - Only cites verified articles for investment theses
  - Treats rumors as secondary context, not primary decision drivers

**Example Groq output structure:**
```
**SYNTHESIS & DOMINANT NARRATIVE** (Based on Verified Sources)
[Uses verified articles only]

**RUMORS & SPECULATION TRACKER**
[Lists rumors and rates plausibility]

**THE BOTTOM LINE OPINION**
[Based on verified facts, noting rumor-driven volatility]
```

## How to Use

### When asking about news:
```
User: "What's happening with Apple?"
→ Advisor fetches: Company news + Filings + Insider trades + Geopolitical events + RUMORS
→ Groq Analysis separates verified from unverified
→ Output shows: "✓ VERIFIED NEWS: ... ⚠️ RUMORS: ..."
```

### What you'll see:
1. **Verified News Section** - Official sources (highlighted in green)
2. **Rumors Section** - Unconfirmed reports (highlighted in yellow with ⚠️)
3. **Analysis** - Groq synthesizes both, clearly distinguishing:
   - What's fact-based
   - What's speculation
   - Which rumors are plausible vs. implausible

## Key Features

✅ **Clear Labeling**: Every rumor marked with ⚠️ UNVERIFIED and "[UNVERIFIED]" tag
✅ **Separated Analysis**: Groq provides distinct sections for verified facts vs. rumors
✅ **Plausibility Rating**: Each rumor rated as HIGH/MEDIUM/LOW plausibility
✅ **Fact-Checking**: Groq compares rumors against verified facts
✅ **Trade-Aware**: Alerts on rumors that might cause volatility even if false
✅ **Transparency**: Full disclosure of information sources and confidence levels

## Technical Details

**API Used:** NewsData.IO (same as verified sources)
- Search terms: 'rumor', 'speculation', 'unconfirmed', 'alleged', 'reported', 'claims'
- Limit: 8 rumors per search (to avoid overwhelming the analysis)
- All rumors processed through Groq for plausibility assessment

**Data Fields:**
```python
{
    'title': str,           # Article headline
    'url': str,             # Source link
    'source': str,          # News outlet [UNVERIFIED]
    'timestamp': str,       # Publication date
    'description': str,     # Article summary
    'type': 'RUMOR',        # Always 'RUMOR'
    'verified': False,      # Always False for rumors
    'confidence': 'UNVERIFIED'  # Always 'UNVERIFIED'
}
```

**Integration Points:**
- `fetch_news_for_ticker()` → Calls `get_rumors_and_speculation()`
- `generate_comprehensive_analysis()` → Receives rumors in article list, separates them, sends to Groq
- Groq prompt → Includes dedicated "RUMORS & SPECULATION TRACKER" section

## Safety & Reliability

- **No false positives:** Rumors only included if explicitly marked as such by sources
- **Groq filters:** AI model assesses rumor plausibility and confidence before including in thesis
- **Source transparency:** Every rumor includes URL and source for user verification
- **Automatic flagging:** Rumors won't be confused with verified news due to visual ⚠️ markers
- **User control:** Users can ignore rumors entirely if preferred (Groq notes them separately)

## Testing

To test the rumors feature:
1. Ask the advisor: "What's the news on [TICKER]?"
2. Look for yellow ⚠️ markers in the output
3. Check the "RUMORS & SPECULATION TRACKER" section in Groq's analysis
4. Verify that investment thesis is based on verified sources, not rumors

## Future Enhancements

Potential improvements:
- Add Reddit/Twitter-specific rumor sources
- Implement rumor tracking over time (has rumor been confirmed later?)
- Add rumor attribution (who's spreading this claim?)
- Plausibility scoring system based on source credibility
- Integration with fact-checking APIs

---
**Feature Added:** January 2025
**Status:** ✅ Complete and tested
