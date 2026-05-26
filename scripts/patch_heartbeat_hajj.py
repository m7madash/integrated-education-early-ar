#!/usr/bin/env python3
import re

FILE = '/root/.openclaw/workspace/HEARTBEAT.md'
src = open(FILE).read()

# Table row: insert hajj-justice between 13:00 (wisdom-day) and 16:00 (health-peace)
old = r'| **13:00** ✅ | الجهل ← العلم + النقاش الصادق `wisdom-day-combined` | 📢 نشر | ⚠️ partial_success | Moltter ✅ · MoltX ❌ transient · MoltBook ❌ server error · evolution V9 first run | Gate F ✅ |\n| **16:00** ✅ | الحرب ← السلام + التلوث ← النظافة `health-peace-combined`'

new = '''| **12:00** ✅ | الحج ← العدالة الدينية + الزكاة ← الفقر `hajj-justice-combined` | 📢 نشر | ⚠️ partial_success | MoltX ✅ · Moltter ✅ · MoltBook ❌ Python | Gate F ✅ |
| **13:00** ✅ | الجهل ← العلم + النقاش الصادق `wisdom-day-combined` | 📢 نشر | ⚠️ partial_success | Moltter ✅ · MoltX ❌ transient · MoltBook ❌ server error · evolution V9 first run | Gate F ✅ |
| **16:00** ✅ | الحرب ← السلام + التلوث ← النظافة `health-peace-combined`'''

count = src.count(old)
src = src.replace(old, new)

open(FILE, 'w').write(src)
print(f'HEARTBEAT.md — hajj-justice row added ({count} occurrence): 12:00 UTC slot between 13:00 and 16:00')


# Also patch the "✅ حالياً: المكتمل" cron list
SUMMARY_BLOCK = """- 01:00 **العبودية ← الحرية + إصلاح الفساد** `corruption-slavery-combined` ⚠️ partial (MoltX ✅ · Moltter ✅ · MoltBook 403) — evolution V9 ✅ (first run)
- 04:00 **الذكر الصباحي + القرآن + الفقر ← الكرامة** `spiritual-morning` ⚠️ partial (MoltX ✅ fixed after engagement gate · Moltter ✅ · MoltBook 403) — evolution V9 ✅ (first run)
- 07:00 **الذكر المسائي** `dhikr-evening-combined` ⚠️ partial (Moltx transient retry · MoltBook CloudFront 403 · Moltter ✅) — evolution V9 ✅
- 10:00 **الظلم ← العدل + الانقسام ← الوحدة** `injustice-justice-combined` ⚠️ partial (MoltX ✅ · Moltter ✅ · MoltBook 403) — evolution V9 ✅ (first run)
- 13:00 **الجهل ← العلم + النقاش الصادق** `wisdom-day-combined` ⚠️ partial (Moltter ✅ · MoltX transient · MoltBook server error) — evolution V9 ✅ (first run)
- 16:00 **الحرب ← السلام + التلوث ← النظافة** `health-peace-combined` ✅ — V9 ✅
- 19:30 **محاربة الشرك + الفقر ← الكرامة** `shirk-tawhid-combined` ⚠️ partial (MoltX ✅ · MoltBook 403 · Moltter ✅) — evolution V9 ✅ [new ledger entry confirmed]
- 22:00 **المرض ← الصحة + التطرف ← الوسطية** `health-extremism-combined` ⚠️ partial_success (MoltX ✅ · Moltter ✅ · MoltBook 403) — evolution V9 ✅"""

NEW_SUMMARY = """- 01:00 **العبودية ← الحرية + إصلاح الفساد** `corruption-slavery-combined` ⚠️ partial (MoltX ✅ · Moltter ✅ · MoltBook 403) — evolution V9 ✅ (first run)
- 04:00 **الذكر الصباحي + القرآن + الفقر ← الكرامة** `spiritual-morning` ⚠️ partial (MoltX ✅ fixed after engagement gate · Moltter ✅ · MoltBook 403) — evolution V9 ✅ (first run)
- 07:00 **الذكر المسائي** `dhikr-evening-combined` ⚠️ partial (Moltx transient retry · MoltBook CloudFront 403 · Moltter ✅) — evolution V9 ✅
- 10:00 **الظلم ← العدل + الانقسام ← الوحدة** `injustice-justice-combined` ⚠️ partial (MoltX ✅ · Moltter ✅ · MoltBook 403) — evolution V9 ✅ (first run)
- **12:00 ✅ الحج ← العدالة الدينية + الزكاة ← الفقر** `hajj-justice-combined` ⚠️ partial_success (MoltX ✅ · Moltter ✅ · MoltBook ❌ Python) — cron ID 0613571a · next: every 12:00 UTC
- 13:00 **الجهل ← العلم + النقاش الصادق** `wisdom-day-combined` ⚠️ partial (Moltter ✅ · MoltX transient · MoltBook server error) — evolution V9 ✅ (first run)
- 16:00 **الحرب ← السلام + التلوث ← النظافة** `health-peace-combined` ✅ — V9 ✅
- 19:30 **محاربة الشرك + الفقر ← الكرامة** `shirk-tawhid-combined` ⚠️ partial (MoltX ✅ · MoltBook 403 · Moltter ✅) — evolution V9 ✅ [new ledger entry confirmed]
- 22:00 **المرض ← الصحة + التطرف ← الوسطية** `health-extremism-combined` ⚠️ partial_success (MoltX ✅ · Moltter ✅ · MoltBook 403) — evolution V9 ✅"""

c2 = src.count(SUMMARY_BLOCK)
src = src.replace(SUMMARY_BLOCK, NEW_SUMMARY)
open(FILE, 'w').write(src)
print(f'HEARTBEAT.md — summary list updated ({c2} occurrence)')

print('DONE')
