#!/usr/bin/env python3
content = open('/root/.openclaw/workspace/missions/war_peace_ultratiny_ar.md', 'r', encoding='utf-8').read()
lines = content.split('\n')
display_chars = 0
for line in lines:
    stripped = line.lstrip('# 🔍 📊 🔍 ✅ 🎓 🕌 💡 💬 🏛️ ⚖️ 🌍 📈 ⚠️ ✅ ❌ ⏳ ⏰ 📡 🗑️')
    if stripped and not line.startswith('```'):
        display_chars += len(stripped)
print(f'Display characters (est): {display_chars}')
print(f'Full length (bytes): {len(content)}')