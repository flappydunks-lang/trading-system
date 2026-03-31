"""
Revert system prompt to natural paragraph style, fix relevance, add geopolitical RSS sources.
"""

filepath = r"c:\Users\aravn\Trading.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# ─── FIX 1: Revert system prompt to paragraph style ───
# Find the system prompt
old_prompt_start = 'system_prompt = f"""You are a professional AI trading analyst. Current date: {current_date}'
old_prompt_end = '"I expect gold to reach $2,100 with 67% confidence based on my analysis." \xe2\x86\x90 WRONG. Fake precision, prediction instead of scenarios.\n"""'

idx_start = content.find(old_prompt_start)
idx_end = content.find(old_prompt_end)

if idx_start < 0:
    print("ERROR: Could not find system prompt start")
    exit(1)
if idx_end < 0:
    # Try without the arrow character
    old_prompt_end2 = '67% confidence based on my analysis.'
    idx_end = content.find(old_prompt_end2, idx_start)
    if idx_end < 0:
        print("ERROR: Could not find system prompt end")
        exit(1)
    # Find the end of the triple-quote line
    idx_end = content.find('"""', idx_end)
    if idx_end < 0:
        print("ERROR: Could not find closing triple quotes")
        exit(1)
    idx_end += 3  # include the """
else:
    idx_end += len(old_prompt_end)

old_prompt = content[idx_start:idx_end]
print(f"Found system prompt: {len(old_prompt)} chars, pos {idx_start}-{idx_end}")

new_prompt = '''system_prompt = f"""You are a professional AI trading analyst. Current date: {current_date}

WHEN USER ASKS GENERAL QUESTIONS (e.g., "what day is it", "who is president", "how are you"):
- Answer them directly and helpfully. Be conversational.

WHEN USER ASKS ABOUT MARKETS, STOCKS, OR CURRENT EVENTS:

Write in natural paragraphs. Be direct and specific. Answer the actual question first.

PARAGRAPH 1 - WHAT'S HAPPENING:
Start by directly answering what the user asked. Summarize the key facts from the news articles provided. Cite sources by name. If you have URLs from the articles, include them. Do NOT invent or fabricate URLs — only use URLs that appear in the provided data.

PARAGRAPH 2 - WHY IT MATTERS:
Explain the cause-and-effect chain. How does this event affect markets, sectors, or the specific asset? Be specific about the mechanism — don't just say "this is bad for stocks," explain WHY.

PARAGRAPH 3 - WHAT COULD HAPPEN NEXT:
Lay out realistic scenarios. What happens if the situation escalates? What happens if it resolves? What are the key things to watch? Include relevant price levels or technical data if provided.

IMPORTANT RULES:
- ANSWER THE USER'S ACTUAL QUESTION FIRST. If they ask about Trump and Iran, talk about Trump and Iran — don't pivot to generic market analysis.
- Use ONLY the live data and articles provided in [REAL DATA FROM YOUR ENGINE]. Those are current as of today.
- NEVER fabricate URLs, prices, percentages, or statistics not in the provided data.
- NEVER say "I predict" or give fake confidence percentages like "73% confident."
- If articles are thin or missing, say so honestly — don't fill gaps with made-up data.
- Cite sources by name when available (e.g., "according to Reuters" or "per AP").
- NEVER ask the user questions or offer to do more things.
- If the user asks about geopolitics/politics, lead with the geopolitical answer, then mention market implications if relevant.

SOURCE TRUST:
- Reuters, AP, Bloomberg, SEC filings = HIGH trust
- Finnhub, CNBC, MarketWatch = MEDIUM trust
- Web scrapes, DuckDuckGo = LOW trust (note the source)
- Rumors = flag as unverified
"""'''

content = content[:idx_start] + new_prompt + content[idx_end:]
changes += 1
print("FIX 1: System prompt reverted to natural paragraph style")

# ─── FIX 2: Fix data injection for non-ticker queries ───
# Remove the rigid format instruction for non-ticker queries
old_nonticker_format = 'full_message += f"\\n6. Use your structured response format: VERIFIED FACTS, WHAT THIS MEANS, SCENARIOS (if market-relevant), CONFIDENCE."'
new_nonticker_format = 'full_message += f"\\n6. Write in natural paragraphs. Answer the question directly first, then explain why it matters, then what could happen next."'

if old_nonticker_format in content:
    content = content.replace(old_nonticker_format, new_nonticker_format)
    changes += 1
    print("FIX 2a: Non-ticker format instruction updated to paragraphs")

# Also fix ticker format instruction
old_ticker_format = 'full_message += f"\\n6. Use your structured response format: VERIFIED FACTS, WHAT THIS MEANS, MARKET SCENARIOS, TECHNICALS, CONFIDENCE."'
new_ticker_format = 'full_message += f"\\n6. Write in natural paragraphs. Start with the key facts, then explain the mechanism, then lay out scenarios with price levels."'

if old_ticker_format in content:
    content = content.replace(old_ticker_format, new_ticker_format)
    changes += 1
    print("FIX 2b: Ticker format instruction updated to paragraphs")

# ─── FIX 3: Add geopolitical RSS sources ───
old_feeds = '''feeds = {
                "Reuters Markets": "https://feeds.reuters.com/reuters/marketsNews",
                "Reuters Top News": "https://feeds.reuters.com/reuters/topNews",
                "CNBC Top News": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
                "Yahoo Finance": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US",
                "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
                "Barrons": "https://www.barrons.com/rss",
                "Motley Fool": "https://www.fool.com/a/feeds/foolwire.aspx",
                "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
            }'''

new_feeds = '''feeds = {
                "Reuters Markets": "https://feeds.reuters.com/reuters/marketsNews",
                "Reuters Top News": "https://feeds.reuters.com/reuters/topNews",
                "Reuters World": "https://feeds.reuters.com/Reuters/worldNews",
                "AP Top News": "https://rsshub.app/apnews/topics/apf-topnews",
                "AP Politics": "https://rsshub.app/apnews/topics/apf-politics",
                "CNBC Top News": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
                "CNBC World": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
                "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
                "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
                "BBC Middle East": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
                "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
                "Yahoo Finance": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US",
                "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
                "NPR News": "https://feeds.npr.org/1001/rss.xml",
                "Guardian World": "https://www.theguardian.com/world/rss",
            }'''

if old_feeds in content:
    content = content.replace(old_feeds, new_feeds)
    changes += 1
    print("FIX 3: Added geopolitical RSS sources (Reuters World, AP, BBC World/MidEast, Al Jazeera, NPR, Guardian)")
else:
    print("WARNING: Could not find RSS feeds block")

# ─── FIX 4: Make the non-ticker data injection prioritize answering the question ───
old_inject_1 = 'full_message += f"\\n2. Answer the user\'s question using the live news articles provided. Cite specific articles by title."'
new_inject_1 = 'full_message += f"\\n2. ANSWER THE USER\'S ACTUAL QUESTION FIRST. If they asked about Iran, lead with Iran. Cite articles by title when referencing them."'

if old_inject_1 in content:
    content = content.replace(old_inject_1, new_inject_1)
    changes += 1
    print("FIX 4: Made data injection prioritize answering the actual question")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nDone. {changes} fixes applied.")
