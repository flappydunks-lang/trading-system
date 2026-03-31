"""Fix double-encoded UTF-8 emojis in Trading.py.

The file has emojis that went through: UTF-8 bytes -> decoded as CP1252 -> re-encoded as UTF-8.
This produces mojibake like "ðŸ"·" instead of the correct emoji.
Fix: for each line, try encode('cp1252').decode('utf-8'). If it succeeds AND changes the line,
the line had mojibake. If it fails, the line has content that can't roundtrip (likely correct 
UTF-8 or mixed), so leave it alone.
"""

filepath = r"c:\Users\aravn\Trading.py"

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

fixed_count = 0
fixed_lines = []

for i, line in enumerate(lines):
    try:
        candidate = line.encode("cp1252").decode("utf-8")
        if candidate != line:
            fixed_lines.append(candidate)
            fixed_count += 1
        else:
            fixed_lines.append(line)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Line has chars that can't encode to CP1252 - leave it as-is
        fixed_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print(f"Fixed {fixed_count} double-encoded lines out of {len(lines)} total.")
print("File saved.")
