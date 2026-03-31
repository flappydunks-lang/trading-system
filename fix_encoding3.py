"""Direct byte-level fix for remaining double-encoded emojis.
Decode the known garbled byte sequences back to correct UTF-8 emojis."""

filepath = r"c:\Users\aravn\Trading.py"

with open(filepath, "rb") as f:
    data = f.read()

original_len = len(data)

# Each entry: (garbled bytes in file, correct UTF-8 emoji bytes)
# Formula: orginal UTF-8 emoji bytes -> interpreted as CP1252 chars -> re-encoded as UTF-8
# To fix: find the re-encoded bytes in file, replace with original emoji bytes

replacements = [
    # 🔍 U+1F50D (magnifying glass) - Market Scanner
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xc2\x8d', b'\xf0\x9f\x94\x8d'),
    
    # 👁️ U+1F441 U+FE0F (eye + variation selector) - Watchlist
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x98\xc2\x81\xc3\xaf\xc2\xb8\xc2\x8f', b'\xf0\x9f\x91\x81\xef\xb8\x8f'),
    
    # 🏢 U+1F3E2 (office building) - Smart Money
    (b'\xc3\xb0\xc5\xb8\xc2\x8f\xc2\xa2', b'\xf0\x9f\x8f\xa2'),
    
    # ⏱️ U+23F1 U+FE0F (stopwatch + variation) - Multi-Timeframe  
    (b'\xc3\xa2\xc2\x8f\xc2\xb1\xc3\xaf\xc2\xb8\xc2\x8f', b'\xe2\x8f\xb1\xef\xb8\x8f'),
    
    # 🏛️ U+1F3DB U+FE0F (classical building + variation) - Political
    (b'\xc3\xb0\xc5\xb8\xc2\x8f\xe2\x80\xba\xc3\xaf\xc2\xb8\xc2\x8f', b'\xf0\x9f\x8f\x9b\xef\xb8\x8f'),
    
    # 📝 U+1F4DD (memo) - Paper Trading
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\x9d', b'\xf0\x9f\x93\x9d'),
    
    # ⚙️ U+2699 U+FE0F (gear + variation) - Settings
    (b'\xe2\x9a\x99\xc3\xaf\xc2\xb8\xc2\x8f', b'\xe2\x9a\x99\xef\xb8\x8f'),
    
    # 🗑️ U+1F5D1 U+FE0F (wastebasket + variation) - Delete User
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x94\xe2\x80\x98\xc3\xaf\xc2\xb8\xc2\x8f', b'\xf0\x9f\x97\x91\xef\xb8\x8f'),

    # 🖥️ U+1F5A5 U+FE0F (desktop computer + variation)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x93\xc2\xa5\xc3\xaf\xc2\xb8\xc2\x8f', b'\xf0\x9f\x96\xa5\xef\xb8\x8f'),
    
    # 🔥 (fire)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xc2\xa5', b'\xf0\x9f\x94\xa5'),
    
    # 🧊 (ice cube)  
    (b'\xc3\xb0\xc5\xb8\xc2\xa7\xc2\x8a', b'\xf0\x9f\xa7\x8a'),
    
    # 🌍 (globe)
    (b'\xc3\xb0\xc5\xb8\xc2\x8c\xc2\x8d', b'\xf0\x9f\x8c\x8d'),
    
    # 📉 (chart decreasing)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\x89', b'\xf0\x9f\x93\x89'),
    
    # 📈 (chart increasing)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\x88', b'\xf0\x9f\x93\x88'),
    
    # 🏦 (bank)
    (b'\xc3\xb0\xc5\xb8\xc2\x8f\xc2\xa6', b'\xf0\x9f\x8f\xa6'),

    # Variation selector alone garbled: ï¸ -> proper VS16
    # This catches remaining \xc3\xaf\xc2\xb8\xc2\x8f that aren't part of larger sequences
    # (b'\xc3\xaf\xc2\xb8\xc2\x8f', b'\xef\xb8\x8f'),
]

fixed_count = 0
for old_bytes, new_bytes in replacements:
    count = data.count(old_bytes)
    if count > 0:
        data = data.replace(old_bytes, new_bytes)
        fixed_count += count
        # Try to show what we replaced
        try:
            emoji = new_bytes.decode('utf-8')
            print(f"  Replaced {count}x -> {emoji}")
        except:
            print(f"  Replaced {count}x ({new_bytes.hex()})")

# Also do a general sweep: find any remaining double-encoded sequences
# by looking for the telltale \xc3\xb0\xc5\xb8 prefix (ð Ÿ in UTF-8 = double-encoded F0 9F prefix)
remaining = data.count(b'\xc3\xb0\xc5\xb8')
if remaining > 0:
    print(f"\n  WARNING: {remaining} remaining \\xc3\\xb0\\xc5\\xb8 sequences (double-encoded emoji prefix)")
    # Show context for each
    start = 0
    shown = 0
    while shown < 10:
        idx = data.find(b'\xc3\xb0\xc5\xb8', start)
        if idx < 0:
            break
        context = data[idx:idx+20]
        print(f"    at {idx}: {context.hex()}")
        start = idx + 1
        shown += 1

# Check for garbled variation selector pattern
remaining_vs = data.count(b'\xc3\xaf\xc2\xb8\xc2\x8f')
if remaining_vs > 0:
    print(f"  WARNING: {remaining_vs} remaining garbled variation selectors")

with open(filepath, "wb") as f:
    f.write(data)

print(f"\nDone. Fixed {fixed_count} emoji sequences. File size: {original_len} -> {len(data)} bytes.")
