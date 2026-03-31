"""Rewrite build_fallback_reasoning and build_event_paragraphs to use scenario format."""
import re

filepath = r"c:\Users\aravn\Trading.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# ─── Fix build_fallback_reasoning ───
# Find the function body from "def build_fallback_reasoning" to the next "def " at the same indent
pattern_fallback = r'(        def build_fallback_reasoning\(ticker: str, tech_context: str, news_items: List\[Dict\[str, str\]\]\) -> str:.*?)(\n        def _parse_datetime)'
match_fb = re.search(pattern_fallback, content, re.DOTALL)
if not match_fb:
    print("ERROR: Could not find build_fallback_reasoning function")
    exit(1)

print(f"Found build_fallback_reasoning at position {match_fb.start()}, length {len(match_fb.group(1))}")

new_fallback = '''        def build_fallback_reasoning(ticker: str, tech_context: str, news_items: List[Dict[str, str]]) -> str:
            """Create a structured, scenario-based response when AI output is non-specific."""
            summary_parts = []

            # Parse technical signals
            rsi_val = None
            daily_trend = None
            weekly_trend = None
            support = None
            resistance = None

            for line in (tech_context or "").splitlines():
                if "RSI:" in line:
                    try:
                        rsi_val = float(line.split("RSI:")[-1].strip())
                    except Exception:
                        pass
                if "Daily Trend:" in line:
                    daily_trend = line.split("Daily Trend:")[-1].strip()
                if "Weekly Trend:" in line:
                    weekly_trend = line.split("Weekly Trend:")[-1].strip()
                if "Support:" in line:
                    support = line.split("Support:")[-1].strip()
                if "Resistance:" in line:
                    resistance = line.split("Resistance:")[-1].strip()

            if daily_trend or weekly_trend:
                summary_parts.append(f"{ticker} is trending {daily_trend or weekly_trend}.".strip())
            if rsi_val is not None:
                summary_parts.append(f"RSI is {rsi_val:.1f}, signaling {'oversold' if rsi_val < 30 else 'overbought' if rsi_val > 70 else 'neutral'} momentum.")

            if not summary_parts:
                summary_parts.append(f"{ticker} has limited confirmed catalysts from available sources.")

            # ── VERIFIED FACTS ──
            facts_section = []
            event_keywords = [
                "rate", "rates", "inflation", "fed", "fomc", "jobs", "cpi", "ppi",
                "earnings", "guidance", "forecast", "downgrade", "upgrade", "lawsuit",
                "antitrust", "sanctions", "tariffs", "deal", "acquisition", "merger",
                "contract", "award", "budget", "shutdown", "security", "breach",
                "cyberattack", "regulation", "policy", "election", "war", "conflict",
                "export controls", "supply chain", "outage", "opec"
            ]

            def _headline_score(it):
                title = (it.get('title') or "").lower()
                source = (it.get('source') or "").lower()
                url = (it.get('url') or "").lower()
                sc = 0
                if any(ev in title for ev in event_keywords):
                    sc += 4
                if any(bad in url for bad in ["health.", "lifestyle", "travel", "food", "sports"]):
                    sc -= 5
                if any(bad in source for bad in ["health", "lifestyle", "sports", "recipes"]):
                    sc -= 5
                return sc

            ranked = sorted(news_items, key=_headline_score, reverse=True) if news_items else []
            picked_items = [it for it in ranked if _headline_score(it) >= 2][:3]

            if picked_items:
                for picked in picked_items:
                    headline = picked.get('title', 'Recent macro/sector headline')
                    src = picked.get('source', 'News')
                    facts_section.append(f"- {headline} (Source: {src})")
            else:
                facts_section.append("- No verified event-driven headlines found in available sources for the past 7 days.")

            # ── WHAT THIS MEANS ──
            interpretation = []
            if picked_items:
                for picked in picked_items:
                    headline_l = (picked.get('title') or '').lower()
                    if any(k in headline_l for k in ["rates", "rate hike", "inflation", "fed", "yield", "fomc"]):
                        interpretation.append(f"- Higher-rate expectations compress valuations for long-duration growth stocks, which can pressure {ticker.upper()} even without company-specific news.")
                    elif any(k in headline_l for k in ["recession", "slowdown", "economy", "growth fears", "jobs", "cpi", "ppi"]):
                        interpretation.append(f"- Macro slowdown or inflation fears drive de-risking, pulling capital from growth names into safer assets.")
                    elif any(k in headline_l for k in ["nasdaq", "tech", "software", "ai", "semiconductor", "cloud"]):
                        interpretation.append(f"- Sector-wide moves spill into correlated names, dragging {ticker.upper()} with peers.")
                    elif any(k in headline_l for k in ["war", "conflict", "sanctions", "tariffs", "geopolitical", "export controls"]):
                        interpretation.append("- Geopolitical stress raises risk premiums and can compress multiples for growth stocks.")
                    elif any(k in headline_l for k in ["defense", "government", "budget", "contract", "shutdown"]):
                        interpretation.append(f"- Government spending uncertainty can weigh on sentiment for contractors and related tech vendors.")
            if not interpretation:
                interpretation.append(f"- Without clear catalysts, {ticker.upper()} is likely driven by broader market positioning and technical levels.")

            # ── SCENARIOS ──
            scenarios = []
            if rsi_val is not None and rsi_val < 30:
                scenarios.append(f"BULL CASE: Oversold RSI ({rsi_val:.1f}) suggests a relief bounce is possible if selling pressure exhausts. Watch for reversal patterns." + (f" Resistance at {resistance} would be the first target." if resistance else ""))
                scenarios.append(f"BEAR CASE: Oversold conditions can persist in strong downtrends." + (f" A break below {support} would signal further downside." if support else " No clear support identified."))
                scenarios.append("BASE CASE: Consolidation near current levels until a catalyst emerges.")
            elif rsi_val is not None and rsi_val > 70:
                scenarios.append(f"BULL CASE: Strong momentum can stay overbought longer than expected." + (f" A break above {resistance} would signal continuation." if resistance else ""))
                scenarios.append(f"BEAR CASE: Overbought RSI ({rsi_val:.1f}) raises pullback risk." + (f" Profit-taking could pull price toward {support}." if support else " Watch for reversal patterns."))
                scenarios.append("BASE CASE: Consolidation or minor pullback before next directional move.")
            elif daily_trend and "up" in daily_trend.lower():
                scenarios.append(f"BULL CASE: Uptrend intact." + (f" Dips toward {support} could attract buyers targeting {resistance}." if support and resistance else " Continuation likely if trend holds."))
                scenarios.append(f"BEAR CASE:" + (f" A break below {support} would negate the bullish structure." if support else " A trend reversal would shift the outlook."))
                scenarios.append("BASE CASE: Trend continuation with normal pullbacks along the way.")
            elif daily_trend and "down" in daily_trend.lower():
                scenarios.append(f"BULL CASE:" + (f" A break above {resistance} would signal potential trend reversal." if resistance else " A reversal pattern would shift outlook."))
                scenarios.append(f"BEAR CASE: Downtrend persists." + (f" Rallies toward {resistance} may face selling pressure." if resistance else " Lower lows likely without catalyst."))
                scenarios.append("BASE CASE: Continued downward drift until macro or company catalyst emerges.")
            else:
                scenarios.append(f"BULL CASE:" + (f" A break above {resistance} with volume would signal bullish momentum." if resistance else " A positive catalyst could trigger upside."))
                scenarios.append(f"BEAR CASE:" + (f" A break below {support} would open further downside." if support else " Negative news could trigger selling."))
                scenarios.append("BASE CASE: Range-bound action likely until a catalyst emerges.")

            # ── TECHNICALS ──
            tech_section = []
            if rsi_val is not None:
                tech_section.append(f"- RSI: {rsi_val:.1f} ({'oversold' if rsi_val < 30 else 'overbought' if rsi_val > 70 else 'neutral'})")
            if daily_trend:
                tech_section.append(f"- Daily Trend: {daily_trend}")
            if weekly_trend:
                tech_section.append(f"- Weekly Trend: {weekly_trend}")
            if support:
                tech_section.append(f"- Support: {support}")
            if resistance:
                tech_section.append(f"- Resistance: {resistance}")
            if not tech_section:
                tech_section.append("- Limited technical data available.")

            # ── CONFIDENCE ──
            confidence = "LOW"
            if picked_items and rsi_val is not None:
                confidence = "MEDIUM"
            if len(picked_items) >= 2 and rsi_val is not None and (support or resistance):
                confidence = "MEDIUM"

            # ── BUILD OUTPUT ──
            summary = " ".join(summary_parts).strip()
            output = f"{summary}\\n\\n"
            output += "VERIFIED FACTS:\\n" + "\\n".join(facts_section) + "\\n\\n"
            output += "WHAT THIS MEANS:\\n" + "\\n".join(interpretation) + "\\n\\n"
            output += "SCENARIOS:\\n" + "\\n".join(f"- {s}" for s in scenarios) + "\\n\\n"
            output += "TECHNICALS:\\n" + "\\n".join(tech_section) + "\\n\\n"
            output += f"CONFIDENCE: {confidence}"

            return output
'''

content = content[:match_fb.start()] + new_fallback + "\n" + match_fb.group(2) + content[match_fb.end():]
print("SUCCESS: build_fallback_reasoning rewritten with scenario format")

# ─── Fix build_event_paragraphs conclusion ───
# Replace the prediction-style conclusion
old_conclusion = '''                conclusion = "\\n\\n**What's next:** The stock is reacting to macro/sector pressures rather than company-specific news. Short-term volatility likely continues until either: (1) a company-specific catalyst emerges, or (2) the broader macro picture stabilizes. Watch key technical levels for breakout/breakdown signals."
                return "\\n\\n".join(paragraphs) + conclusion'''

new_conclusion = '''                conclusion = "\\n\\nNOTE: The stock appears to be reacting to macro/sector pressures rather than company-specific news. Monitor key technical levels and upcoming catalysts for directional signals."
                return "\\n\\n".join(paragraphs) + conclusion'''

if old_conclusion in content:
    content = content.replace(old_conclusion, new_conclusion)
    print("SUCCESS: build_event_paragraphs conclusion updated")
else:
    print("WARNING: Could not find build_event_paragraphs conclusion to replace")
    # Try to find it with a broader search
    if "What's next:** The stock is reacting" in content:
        print("  Found the text but quoting mismatch - trying alternate approach")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("File saved.")
