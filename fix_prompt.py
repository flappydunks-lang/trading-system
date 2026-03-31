import re

with open(r'c:\Users\aravn\Trading.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the analysis_prompt
old_start = 'analysis_prompt = f"""{price_context}You are analyzing {verified_count} VERIFIED news articles'
old_end = 'based on real evidence."""'

start_idx = content.find(old_start)
end_idx = content.find(old_end, start_idx)

if start_idx == -1:
    print("ERROR: Could not find start marker")
    exit(1)
if end_idx == -1:
    print("ERROR: Could not find end marker")
    exit(1)

end_idx += len(old_end)

print(f"Found prompt at chars {start_idx}-{end_idx} (length {end_idx - start_idx})")

new_prompt = '''analysis_prompt = f"""{price_context}You are analyzing {verified_count} news articles about {ticker}, each with a trust score (1-10). Separate FACTS from INTERPRETATION from SCENARIOS.

DATA RULES:
- Price data above is LIVE from Yahoo Finance. Articles are from live APIs.
- Use ONLY the data provided. Do NOT substitute from training data.
- Higher trust score = more weight. LOW TRUST sources need corroboration.

ARTICLES (with trust scores):
{article_list}
{rumor_section}

YOU MUST USE THIS EXACT FORMAT:

📰 VERIFIED FACTS (from articles with trust score 7+ only, or lower if corroborated)
- State each fact with source name, trust score, and link
- NO interpretation here — just what happened
- If only low-trust sources report something, note: "Reported by [source] (trust: X/10) — not independently confirmed"

🧠 WHAT THIS MEANS FOR {ticker}
- For each key fact, explain the cause → effect mechanism
- Be specific: HOW does this impact {ticker}'s revenue, costs, competitive position, or sentiment?
- Skip articles with no plausible connection to {ticker}

⚖️ MARKET SCENARIOS (NOT predictions)
- 🟢 Bull case: "If [condition from news] → [outcome]. Key trigger: [event]"
- 🔴 Bear case: "If [condition from news] → [outcome]. Key trigger: [event]"
- 🟡 Neutral: "If [condition] → sideways. What breaks the range: [catalyst]"
- Include key price levels for each scenario if technical data is available

📊 TECHNICALS (only if valid data provided above)
- Current price, RSI, trend from LIVE data only
- Support must be BELOW current price — flag invalid otherwise
- Resistance must be ABOVE current price — flag invalid otherwise

🎯 CONFIDENCE
- Rate: LOW / MEDIUM / HIGH (never fake percentages)
- Why: source quality, corroboration, conflicting signals
- Key risks that could invalidate this analysis

Facts are sacred. Interpretation explains mechanism. Scenarios are conditional, never certain."""'''

new_content = content[:start_idx] + new_prompt + content[end_idx:]

with open(r'c:\Users\aravn\Trading.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: Analysis prompt replaced")
