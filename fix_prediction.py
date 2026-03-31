with open(r'c:\Users\aravn\Trading.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the generate_stock_prediction function
marker = 'def generate_stock_prediction(ticker: str, tech_context: str, news_context: str) -> str:'
start_idx = content.find(marker)
if start_idx == -1:
    print("ERROR: Could not find generate_stock_prediction")
    exit(1)

# Find where the function body ends by looking for the return statement
ret_marker = 'return f"\\n[COMBINED ANALYSIS - TECHNICAL + SENTIMENT]:\\n{prediction}"'
end_idx = content.find(ret_marker, start_idx)
if end_idx == -1:
    # Try alternate
    ret_marker = '[COMBINED ANALYSIS - TECHNICAL + SENTIMENT]'
    end_idx = content.find(ret_marker, start_idx)
    if end_idx == -1:
        print("ERROR: Could not find return marker")
        # Show what's around
        print(content[start_idx:start_idx+200])
        exit(1)
    # Find the end of that line
    end_idx = content.find('\n', end_idx)

print(f"Found function at {start_idx}")
print(f"Return marker at {end_idx}")

# Find the part we need to replace: from the function start to just before 'elif use_ollama:'
# We want to replace from the function def through the groq prediction block
end_groq = content.find('elif use_ollama:', start_idx)
if end_groq == -1:
    print("ERROR: Could not find elif use_ollama")
    exit(1)

# Show what we're replacing
print(f"Replacing chars {start_idx} to {end_groq}")
print(f"First 100 chars: {content[start_idx:start_idx+100]}")
print(f"Last 100 chars before marker: {content[end_groq-100:end_groq]}")

# Construct the indentation (8 spaces for the def line inside the outer function)
new_func = '''def generate_stock_prediction(ticker: str, tech_context: str, news_context: str) -> str:
            """Generate scenario analysis: Technical + News sentiment combined."""
            try:
                old_level = logger.level
                logger.setLevel(logging.ERROR)
                
                # STEP 1: Get Groq's news sentiment classification
                news_sentiment_prompt = f"""Analyze the news sentiment for {ticker}:

{news_context}

Provide a SHORT, FOCUSED analysis (3-4 sentences max):
1. Overall news sentiment: bullish, bearish, or mixed?
2. The 1-2 most important catalysts from the news
3. What emotions is this news triggering in the market? (Fear, greed, uncertainty?)
Be specific with facts from the news."""
                
                news_sentiment = ""
                if use_groq:
                    response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": news_sentiment_prompt}],
                        max_tokens=250,
                        temperature=0.4
                    )
                    news_sentiment = response.choices[0].message.content
                
                # STEP 2: Generate scenario-based analysis (NOT predictions)
                combined_prompt = f"""You are a professional market analyst for {ticker}. You NEVER predict prices. You present SCENARIOS.

LIVE TECHNICAL DATA:
{tech_context}

NEWS SENTIMENT:
{news_sentiment}

Use this EXACT format:

SCENARIOS FOR {ticker}:

BULL CASE:
- Condition: "If [specific trigger from news/technicals]..."
- Outcome: What happens and key level to watch
- Probability driver: What makes this more likely

BEAR CASE:
- Condition: "If [specific trigger from news/technicals]..."
- Outcome: What happens and key level to watch
- Probability driver: What makes this more likely

BASE CASE (most likely near-term):
- Current setup: Technical + sentiment alignment or conflict
- Range: Between what levels does price likely consolidate?
- What breaks the range: Specific catalyst needed

TECHNICAL VALIDATION:
- Does the chart support or contradict the news sentiment?
- Key support (must be BELOW price) and resistance (must be ABOVE price)
- If support is above price or resistance below price, flag as INVALID DATA

CONFIDENCE: LOW / MEDIUM / HIGH
- Why this rating (source quality, signal alignment)
- What would change your assessment
- Key risk: one thing that could blow up all scenarios

RULES: No price targets. No 'I predict.' No fake confidence percentages. Only conditional scenarios."""
                
                prediction = ""
                
                if use_groq:
                    response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": combined_prompt}],
                        max_tokens=600,
                        temperature=0.4
                    )
                    prediction = response.choices[0].message.content
                
                '''

new_content = content[:start_idx] + new_func + content[end_groq:]

with open(r'c:\Users\aravn\Trading.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: Stock prediction function rewritten with scenarios")
