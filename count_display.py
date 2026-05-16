#!/usr/bin/env python3
with open('/root/.openclaw/workspace/missions/war_peace_ultratiny_ar.md', encoding='utf-8') as f:
    text = f.read()
# Count all non-whitespace characters and spaces that would display
count = len(text)
print(f'Total display length: {count}')
# Count Arabic script chars specifically
arabic = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
print(f'Arabic letters: {arabic}')
# Emojis
emojis = sum(1 for c in text if ord(c) > 0x1F300 and ord(c) < 0x1F9FF)
print(f'Emojis (approx): {emojis}')
print(text[:400])