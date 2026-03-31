with open(r'c:\Users\aravn\Trading.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Unique anchor: the if-block for news_choice == "6"
# We replace the narrow section from the Back line through the return
# The back-arrow mojibake is: \u00e2\u2020\x90
back_arrow = '\u00e2\u2020\x90'

# OLD: 6 choices, back is option 6, if == "6" returns
old_chunk = (
    f'        console.print("6. {back_arrow} Back\\n")\n'
    '\n'
    '        news_choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6"], default="1")\n'
    '\n'
    '        if news_choice == "6":\n'
    '            return'
)

# NEW: add option 6 political, back becomes 7
new_chunk = (
    '        console.print("6. \U0001f3db\ufe0f  Political News \u2192 Market Impact (Groq AI)")\n'
    f'        console.print("7. {back_arrow} Back\\n")\n'
    '\n'
    '        news_choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")\n'
    '\n'
    '        if news_choice == "7":\n'
    '            return'
)

if old_chunk in content:
    content = content.replace(old_chunk, new_chunk, 1)
    with open(r'c:\Users\aravn\Trading.py', 'w', encoding='utf-8', errors='replace') as f:
        f.write(content)
    print('OK: menu patched')
else:
    # Debug: show what is actually around the news_choice=="6" line
    idx = content.find('        if news_choice == "6":')
    print('news_choice=6 block at char', idx)
    if idx != -1:
        print(repr(content[idx-400:idx+80]))
    else:
        print('not found at all')

# The back-arrow in this file decodes (via mojibake) to \u00e2\u2020\x90
back_arrow = '\u00e2\u2020\x90'

old_lines = (
    '        console.print("5. \u2699\ufe0f  Manage Tracked Twitter/X Accounts")\n'
    f'        console.print("6. {back_arrow} Back\\\\n")\n'
    '\n'
    '        news_choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6"], default="1")\n'
    '\n'
    '        if news_choice == "6":\n'
    '            return'
)

new_lines = (
    '        console.print("5. \u2699\ufe0f  Manage Tracked Twitter/X Accounts")\n'
    '        console.print("6. \U0001f3db\ufe0f  Political News \u2192 Market Impact (Groq AI)")\n'
    f'        console.print("7. {back_arrow} Back\\\\n")\n'
    '\n'
    '        news_choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")\n'
    '\n'
    '        if news_choice == "7":\n'
    '            return'
)

if old_lines in content:
    content = content.replace(old_lines, new_lines, 1)
    with open(r'c:\Users\aravn\Trading.py', 'w', encoding='utf-8', errors='replace') as f:
        f.write(content)
    print('OK: menu patched')
else:
    # Try finding just the distinctive part to debug
    idx = content.find('choices=["1", "2", "3", "4", "5", "6"], default="1"')
    print('choices line at char', idx)
    if idx != -1:
        chunk = content[idx-300:idx+60]
        for i, ch in enumerate(chunk):
            print(i, repr(ch), hex(ord(ch)))
    print('NOT FOUND')

old_lines = (
    '        console.print("5. \u2699\ufe0f  Manage Tracked Twitter/X Accounts")\n'
    '        console.print("6. \u2190 Back\\n")\n'
    '\n'
    '        news_choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6"], default="1")\n'
    '\n'
    '        if news_choice == "6":\n'
    '            return'
)

new_lines = (
    '        console.print("5. \u2699\ufe0f  Manage Tracked Twitter/X Accounts")\n'
    '        console.print("6. \U0001f3db\ufe0f  Political News \u2192 Market Impact (Groq AI)")\n'
    '        console.print("7. \u2190 Back\\n")\n'
    '\n'
    '        news_choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")\n'
    '\n'
    '        if news_choice == "7":\n'
    '            return'
)

if old_lines in content:
    content = content.replace(old_lines, new_lines, 1)
    with open(r'c:\Users\aravn\Trading.py', 'w', encoding='utf-8', errors='replace') as f:
        f.write(content)
    print("OK: menu patched")
else:
    # Try alternate: line 14451 has escaped backslash differently
    # Show surrounding context for debug
    idx = content.find('Manage Tracked Twitter/X Accounts')
    if idx != -1:
        print("CONTEXT:", repr(content[idx-5:idx+300]))
    else:
        print("NOT FOUND at all")
    sys.exit(1)
