"""Fix dead code after raise, lower temperature, reinforce format for non-ticker queries."""
import re

filepath = r"c:\Users\aravn\Trading.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# ─── FIX 1: Lower temperature from 0.75 to 0.4 ───
old_temp = "temperature=0.75"
if old_temp in content:
    # Only replace in the main conversation Groq call (there might be others)
    # The main one is near "model_candidates" and "api_messages"
    # Count occurrences
    count = content.count(old_temp)
    print(f"Found {count} occurrences of temperature=0.75")
    # Replace ALL of them with 0.4
    content = content.replace(old_temp, "temperature=0.4")
    changes += 1
    print("FIX 1: Lowered all temperature=0.75 to 0.4")
else:
    print("SKIP 1: temperature=0.75 not found (may already be changed)")

# ─── FIX 2: Fix dead code after raise ───
# The except block has `raise` followed by unreachable code
# We need to move that code to AFTER the try/except, at the try's indent level
old_dead_code = '''                        raise

                        # CRITICAL: Remove any trailing questions or offers
                        lines = ai_response.split('\\n')
                        cleaned_lines = []
                        for line in lines:
                            # Skip any line that's a question (ends with ?)
                            if line.strip().endswith('?'):
                                continue
                            # Skip lines that offer to do something
                            offer_phrases = ['Want', 'Would', 'Should', 'Let me', 'Let us', 'I could', "I'd love", "I'd be happy", "I'd recommend checking", "I can help", 'Do you want']
                            if any(line.strip().startswith(p) for p in offer_phrases):
                                continue
                            cleaned_lines.append(line)
                        
                        ai_response = '\\n'.join(cleaned_lines).strip()
                        
                        # If response is empty after cleaning, provide default
                        if not ai_response:
                            ai_response = "Based on the data provided, I don't have enough information to give a clear analysis right now."

                        # If response is vague/non-specific, replace with structured fallback
                        vague_markers = [
                            "no direct information",
                            "lack of",
                            "difficult to determine",
                            "no verified",
                            "confidence level in this opinion is 0",
                            "not supported or contradicted",
                            "no specific information"
                        ]
                        if any(m in ai_response.lower() for m in vague_markers):
                            ai_response = build_fallback_reasoning(mentioned_ticker or "This stock", tech_context, stored_news)

                        # Guard against generic model disclaimers
                        disclaimer_markers = [
                            "i don't have access to real-time news",
                            "training data only goes up to",
                            "i don't have the ability to browse"
                        ]
                        if any(m in ai_response.lower() for m in disclaimer_markers):
                            event_text = build_event_paragraphs(mentioned_ticker or "This stock", stored_news)
                            ai_response = event_text or "No verified company-specific catalyst in the past 7 days; price likely driven by broader sector/macro pressure."

                        conversation_history.append({"role": "assistant", "content": ai_response})'''

# The fix: keep only `raise` in the except block, move the rest to after the try/except
# The try block is at 20-space indent, so code after try/except should be at 20-space indent
new_code = '''                        raise

                    # ── POST-PROCESSING (runs after successful Groq response) ──
                    # Remove trailing questions or offers
                    lines = ai_response.split('\\n')
                    cleaned_lines = []
                    for line in lines:
                        if line.strip().endswith('?'):
                            continue
                        offer_phrases = ['Want', 'Would', 'Should', 'Let me', 'Let us', 'I could', "I'd love", "I'd be happy", "I'd recommend checking", "I can help", 'Do you want']
                        if any(line.strip().startswith(p) for p in offer_phrases):
                            continue
                        cleaned_lines.append(line)
                    
                    ai_response = '\\n'.join(cleaned_lines).strip()
                    
                    if not ai_response:
                        ai_response = "Based on the data provided, I don't have enough information to give a clear analysis right now."

                    # If response is vague/non-specific, replace with structured fallback
                    vague_markers = [
                        "no direct information",
                        "lack of",
                        "difficult to determine",
                        "no verified",
                        "confidence level in this opinion is 0",
                        "not supported or contradicted",
                        "no specific information"
                    ]
                    if any(m in ai_response.lower() for m in vague_markers):
                        ai_response = build_fallback_reasoning(mentioned_ticker or "This stock", tech_context, stored_news)

                    # Guard against generic model disclaimers
                    disclaimer_markers = [
                        "i don't have access to real-time news",
                        "training data only goes up to",
                        "i don't have the ability to browse"
                    ]
                    if any(m in ai_response.lower() for m in disclaimer_markers):
                        event_text = build_event_paragraphs(mentioned_ticker or "This stock", stored_news)
                        ai_response = event_text or "No verified company-specific catalyst in the past 7 days; price likely driven by broader sector/macro pressure."

                    conversation_history.append({"role": "assistant", "content": ai_response})'''

if old_dead_code in content:
    content = content.replace(old_dead_code, new_code)
    changes += 1
    print("FIX 2: Moved dead code after raise to proper location (after try/except)")
else:
    print("ERROR 2: Could not find the dead code block")
    # Try to find it partially
    if "raise\n\n                        # CRITICAL: Remove any trailing" in content:
        print("  Found partial match - checking for whitespace issues")

# ─── FIX 3: Reinforce 5-section format for non-ticker queries ───
old_nonticker = '''                        else:
                            full_message += f"\\n2. Answer the user's question using the live news articles provided. Cite specific articles by title and link."
                            full_message += f"\\n3. Summarize what the news says and explain market implications if relevant."
                            full_message += f"\\n4. Do NOT say you don't have real-time information \\xe2\\x80\\x93 the articles above ARE your real-time information."'''

new_nonticker = '''                        else:
                            full_message += f"\\n2. Answer the user's question using the live news articles provided. Cite specific articles by title."
                            full_message += f"\\n3. NEVER fabricate, invent, or guess URLs. Only cite URLs that appear in the articles above. If no URL is provided for an article, do not make one up."
                            full_message += f"\\n4. NEVER invent specific prices, percentages, or statistics. Only cite numbers from the articles above."
                            full_message += f"\\n5. Do NOT say you don't have real-time information. The articles above ARE your real-time information."
                            full_message += f"\\n6. Use your structured response format: VERIFIED FACTS, WHAT THIS MEANS, SCENARIOS (if market-relevant), CONFIDENCE."'''

if old_nonticker in content:
    content = content.replace(old_nonticker, new_nonticker)
    changes += 1
    print("FIX 3: Reinforced format and anti-hallucination for non-ticker queries")
else:
    print("ERROR 3: Could not find non-ticker instructions block")
    # Debug: find the approximate area
    idx = content.find("Answer the user's question using the live news articles")
    if idx >= 0:
        print(f"  Found 'Answer the user's question' at position {idx}")
        snippet = content[idx-100:idx+400]
        print(f"  Context: ...{repr(snippet[:200])}...")
    else:
        print("  'Answer the user's question' not found at all")

# Also reinforce for ticker queries - add anti-hallucination
old_ticker_inst = '''                            full_message += f"\\n4. If an article has no plausible connection to {ticker_label}, skip it entirely rather than forcing a generic link."'''
new_ticker_inst = '''                            full_message += f"\\n4. If an article has no plausible connection to {ticker_label}, skip it entirely rather than forcing a generic link."
                            full_message += f"\\n5. NEVER fabricate URLs. Only cite URLs from the articles above. NEVER invent specific prices or percentages not in the data."
                            full_message += f"\\n6. Use your structured response format: VERIFIED FACTS, WHAT THIS MEANS, MARKET SCENARIOS, TECHNICALS, CONFIDENCE."'''

if old_ticker_inst in content:
    content = content.replace(old_ticker_inst, new_ticker_inst)
    changes += 1
    print("FIX 4: Added anti-hallucination + format reinforcement for ticker queries")
else:
    print("SKIP 4: Ticker instruction not found (may have different text)")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nDone. {changes} fixes applied. File saved.")
