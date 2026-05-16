text = open('/root/.openclaw/workspace/missions/war_peace_moltter_final.txt', encoding='utf-8').read()
print(f"Total chars: {len(text)}")
print(f"Char breakdown:")
for i, c in enumerate(text):
    print(f"{i:3d}: U+{ord(c):04X} {c}")