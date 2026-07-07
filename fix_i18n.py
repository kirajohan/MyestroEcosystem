#!/usr/bin/env python3
import re

with open('telegram_bot/bot/utils/i18n.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 212 (index 211) - remove the backslash-n at end
fixed_lines = []
for i, line in enumerate(lines):
    if i == 212:  # Line 213 (0-indexed)
        # Remove the backslash-n continuation at the end
        line = line.rstrip('\\\n') + '\n'
    fixed_lines.append(line)

with open('telegram_bot/bot/utils/i18n.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed i18n.py")
