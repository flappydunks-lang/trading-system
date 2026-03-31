# Rumors Tracking - Usage Examples

## Example 1: Apple News Query

**User asks:** "What's happening with Apple stock?"

**Expected Output Flow:**

```
🌍 Searching for news on AAPL (Company + Geopolitical + Market)...
✓ Finnhub: 15 company news articles
✓ SEC Edgar: 3 recent filings
✓ Insider Trades: 2 recent trades
✓ NewsData.IO: 10 geopolitical/macro events
⚠️  Rumors/Speculation: 8 unverified reports found
✓ Total: 38 sources compiled

[🤖 GROQ SYNTHESIS OF 30 VERIFIED + 8 RUMOR SOURCES FOR AAPL]

**SYNTHESIS & DOMINANT NARRATIVE** (Based on Verified Sources):
- Consensus: Apple strong earnings miss vs expectations
- Common themes:
  1. iPhone 16 sales underperformance in China (from verified SEC filings + Finnhub)
  2. Services segment growth offset hardware decline (from verified analysis)
  3. China tariff exposure if Trump policies proceed (from NewsData.IO geopolitical)
- Current price action: Down 3.2% today, RSI at 38 (oversold)
- Verified facts align with downward pressure

**RUMORS & SPECULATION TRACKER** (8 Unverified Reports):
1. ⚠️ "Apple planning massive $100B buyback to prop up stock" - Plausibility: LOW
   - Sources: TechRumor, StockTwits speculation
   - Why LOW: No SEC filing, insider transactions don't support this scale

2. ⚠️ "Jobs Book leak: Apple cutting 15% of workforce" - Plausibility: MEDIUM
   - Sources: Anonymous insider claims
   - Why MEDIUM: Aligns with broader tech layoff trend, but unconfirmed

3. ⚠️ "New AirPods Pro 3 launch next month with AI features" - Plausibility: HIGH
   - Sources: Apple supply chain rumors
   - Why HIGH: Consistent with annual refresh cycle, timing matches keynote rumors

4. ⚠️ "Apple paying $25B for AI company X" - Plausibility: LOW
   - Sources: Stocktwits speculation
   - Why LOW: No credible reporting, not aligned with Apple's recent M&A pattern

5-8. [Additional rumors listed with plausibility ratings...]

**THE BOTTOM LINE OPINION** (Combining Verified News + Current Price Action):
- Should AAPL trade UP, DOWN, or SIDEWAYS? **DOWN (confidence: MEDIUM)**
- Conviction level: MEDIUM - Verified facts support weakness, but rumors about buybacks and AI strategy not yet confirmed
- Current price action (RSI=38, -3.2% today) aligns with verified negative sentiment
- Rumors being discussed: buyback support, workforce cuts, product launches - Market is pricing in some of these unknowns
- Could unverified rumors suddenly become reality? Yes - If the "AI strategy" rumors prove true (HIGH plausibility), AAPL could reverse sharply
- What could change my mind: Strong earnings surprise next quarter, or official announcement of new AI products

**SPECIFIC STOCK PRICE DIRECTION WITH TARGETS**:
- Short-term (1-4 weeks): DOWN to $192 support (based on verified earnings miss + oversold RSI setup)
- Medium-term (1-3 months): Neutral, range-bound until new products announced
- Long-term (3+ months): UP if AI initiatives confirmed (rumor-driven upside)

**TRADE SETUP ANALYSIS**:
- Good entry point? Conditionally. RSI at 38 shows oversold bounce opportunity
- But watch for: Confirmation of workforce reduction rumors (could trigger further selloff)
- Support levels: $190, $185 (from recent news catalysts)

**CONFIDENCE & RISKS**:
- Confidence: 65% in downside, 35% in AI-driven upside (if rumors prove true)
- Biggest verified risks: Further China weakness, tariff impact escalation
- Minority opinion in verified sources: 2 analysts remain bullish on Services growth
- Rumor-driven risks: If buyback rumors + workforce rumors both false, stock could gap up 5-8%
```

---

## Example 2: Tesla Stock Check

**User asks:** "Any news about Tesla?"

**Key Output Sections:**

### ✅ VERIFIED NEWS (Sourced)
1. Tesla Q4 deliveries miss targets (from SEC 8-K filing)
2. Elon Musk's xAI funding announcement (from Finnhub, NewsData.IO)
3. Chinese EV tariff threat (from NewsData.IO geopolitical)
4. Insider selling by directors (from Form 4 filings)

### ⚠️ UNVERIFIED RUMORS (Labeled)
1. **"Tesla planning $5B acquisition of battery startup"** - Plausibility: MEDIUM
   - Aligned with verified Musk strategy, but no SEC filing yet
   
2. **"Autopilot safety investigation to be dropped"** - Plausibility: LOW
   - No source, contradicts verified NHTSA ongoing review

3. **"Tesla stock split coming Q2"** - Plausibility: HIGH
   - Matches historical pattern, market sentiment suggests likelihood

### 💡 GROQ ANALYSIS
- Verified thesis: Tesla facing near-term headwinds from deliveries, China tariffs, insider selling
- Rumors being watched: Stock split (HIGH confidence), acquisition (MEDIUM), investigation drop (LOW)
- Investment implication: Don't base thesis on rumors, but stock split rumor could explain buying despite bad news

---

## Example 3: Small Cap Biotech - Highly Speculative

**User asks:** "What's going on with [BIOTECH TICKER]?"

**Output shows:**

### ✅ VERIFIED (Limited - small cap)
- 1 recent SEC filing (quarterly report)
- 2 Finnhub news items about clinical trial updates

### ⚠️ RUMORS (Abundant - biotech heavy on speculation)
- **"FDA approval expected next month"** - Plausibility: MEDIUM
- **"Phase 3 data shows 95% efficacy"** - Plausibility: LOW (no verification yet)
- **"Big pharma acquisition talks underway"** - Plausibility: MEDIUM
- **"Lead researcher leaving the company"** - Plausibility: MEDIUM (unconfirmed)
- 6 additional rumors tracked

### 💡 GROQ ANALYSIS
For small caps, Groq acknowledges:
- Verified data is limited (use caution)
- Rumors form large portion of market narrative
- Stock likely driven by rumor flow vs. verified facts
- Plausibility assessment critical given low transparency
- High volatility expected if rumors confirmed/denied

---

## Visual Indicators

### In Console Output:
- ✅ = Verified news (green)
- ⚠️ = Unverified rumors (yellow)
- 🌍 = Geopolitical/macro (cyan)
- 🤖 = AI synthesis section (highlighted)

### In Analysis Text:
- **VERIFIED ARTICLE #1**: Use for investment thesis
- **⚠️ RUMOR**: Monitor but don't base decisions on
- [UNVERIFIED]: Source field marker for rumors
- Plausibility rating: HIGH/MEDIUM/LOW assessment

---

## Key Takeaways for Users

1. **Green checkmarks = Trust these for decisions**
   - Official filings, company news, insider trades
   - Use for investment thesis

2. **Yellow warnings = Watch but verify**
   - Rumors, speculation, unconfirmed reports
   - Can explain volatility but shouldn't drive decisions

3. **Plausibility ratings = Filter noise**
   - HIGH: Likely to be true, align with facts
   - MEDIUM: Possible, needs confirmation
   - LOW: Unlikely, contradicts verified facts

4. **Groq separates the analysis**
   - Investment thesis based on verified data
   - Rumors acknowledged as potential catalysts
   - Clear risk disclosure for rumor-driven moves
