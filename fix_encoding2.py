"""Fix remaining mojibake emojis that the simple CP1252 roundtrip missed.

These are lines where only SOME characters are double-encoded, mixed with 
properly-encoded text (e.g. escape sequences or ASCII). The approach:
For each line, try to fix character-by-character using a sliding window that 
detects double-encoded UTF-8 sequences and decodes them.
"""

filepath = r"c:\Users\aravn\Trading.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

def fix_mojibake(text):
    """Fix double-encoded UTF-8 (via CP1252) in a string, character by character."""
    result = []
    i = 0
    chars = list(text)
    n = len(chars)
    
    while i < n:
        # Try to detect a double-encoded UTF-8 sequence starting at position i
        # A double-encoded sequence: the original UTF-8 bytes (e.g., F0 9F 93 B7)
        # were interpreted as CP1252 chars, then those chars were UTF-8 encoded.
        # So we try: take a window of chars, encode them as CP1252, see if the 
        # result is valid UTF-8.
        
        found = False
        # Try window sizes 2-8 (double-encoded 2-4 byte UTF-8 chars produce 2-12 chars)
        for window in range(8, 1, -1):
            if i + window > n:
                continue
            chunk = "".join(chars[i:i+window])
            try:
                # Try to encode as CP1252
                raw_bytes = chunk.encode("cp1252")
                # Try to decode those bytes as UTF-8
                decoded = raw_bytes.decode("utf-8")
                # Check that it actually changed something (not just ASCII)
                if decoded != chunk and len(decoded) >= 1:
                    result.append(decoded)
                    i += window
                    found = True
                    break
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
        
        if not found:
            result.append(chars[i])
            i += 1
    
    return "".join(result)

# Process line by line
lines = content.split("\n")
fixed_count = 0
new_lines = []

for idx, line in enumerate(lines):
    # Only process lines that have potential mojibake indicators
    has_mojibake = False
    # Check for common mojibake patterns: high codepoint latin chars that shouldn't be there
    mojibake_chars = [
        "\u00f0",  # ð (from F0)
        "\u00c3",  # Ã (from C3)  
        "\u00e2",  # â (from E2)
        "\u0178",  # Ÿ (from 9F via CP1252)
        "\u201c",  # " (from 93 via CP1252)
        "\u201d",  # " (from 94 via CP1252)
        "\u0152",  # Œ (from 8C via CP1252)
        "\u2019",  # ' (from 92 via CP1252)
    ]
    for mc in mojibake_chars:
        if mc in line:
            has_mojibake = True
            break
    
    if has_mojibake:
        fixed_line = fix_mojibake(line)
        if fixed_line != line:
            fixed_count += 1
            new_lines.append(fixed_line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))

print(f"Fixed {fixed_count} additional mojibake lines.")
print("File saved.")
